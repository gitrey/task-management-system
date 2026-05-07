import logging
import uuid
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .manager import TaskManager
from .models import Task, TaskStatus, TaskCreateRequest, User, Project
from .retry import RetryPolicy
from .persistence import SQLiteStateStore
from .metrics import get_metrics_data
from .auth import create_access_token, decode_access_token, verify_password, get_password_hash
from .ai_service import AIService
from .scheduler import TaskScheduler

app = FastAPI(title="Task Management System API")

# Enable CORS for the web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize Services
store = SQLiteStateStore("tasks.db")
manager = TaskManager(state_store=store)
ai_service = AIService()
scheduler = TaskScheduler(manager)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    user = store.get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/healthz")
async def healthz():
    """Liveness probe."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

@app.get("/readyz")
async def readyz():
    """Readiness probe."""
    components = {
        "database": "disconnected",
        "storage": "readonly"
    }
    is_ready = True
    
    try:
        # Check database connection
        with manager.state_store.conn as conn:
            conn.execute("SELECT 1")
        components["database"] = "connected"
    except Exception:
        components["database"] = "error"
        is_ready = False

    try:
        # Check storage write access
        if os.access(manager.state_store.db_path, os.W_OK):
            components["storage"] = "writable"
        else:
            is_ready = False
    except Exception:
        components["storage"] = "error"
        is_ready = False

    if not is_ready:
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "components": components}
        )

    return {
        "status": "ready",
        "components": components
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    data, content_type = get_metrics_data()
    return Response(content=data, media_type=content_type)

# Authentication Endpoints
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = store.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register(user_data: Dict[str, str]):
    if store.get_user(user_data["username"]):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = User(
        user_id=str(uuid.uuid4()),
        username=user_data["username"],
        email=user_data.get("email"),
        hashed_password=get_password_hash(user_data["password"])
    )
    store.save_user(user)
    return {"message": "User registered successfully"}

# Project Endpoints
@app.get("/api/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    return store.get_user_projects(current_user.user_id)

@app.post("/api/projects")
async def create_project(project_data: Dict[str, str], current_user: User = Depends(get_current_user)):
    project = Project(
        project_id=str(uuid.uuid4()),
        name=project_data["name"],
        owner_id=current_user.user_id
    )
    store.save_project(project)
    return project

# AI Endpoints
@app.post("/api/ai/generate")
async def generate_workflow(request: Dict[str, str], current_user: User = Depends(get_current_user)):
    prompt = request.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    try:
        return await ai_service.generate_dag(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Task Endpoints
@app.get("/api/tasks", response_model=List[Dict[str, Any]])
async def get_tasks(project_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Returns tasks filtered by project and user access."""
    user_projects = store.get_user_projects(current_user.user_id)
    project_ids = [p.project_id for p in user_projects]
    
    if project_id and project_id not in project_ids:
        raise HTTPException(status_code=403, detail="Access denied to project")

    with manager.lock:
        tasks = []
        for t in manager.tasks.values():
            if project_id:
                if t.project_id == project_id:
                    tasks.append(t)
            elif t.project_id in project_ids or t.project_id is None:
                tasks.append(t)
                
        return [
            {
                "id": t.task_id,
                "name": t.name or t.task_id,
                "project_id": t.project_id,
                "priority": t.priority,
                "status": t.status.value,
                "dependencies": list(t.dependencies),
                "dependents": list(t.dependents),
                "result": t.result,
                "error": str(t.error) if t.error else None,
                "trace_id": t.trace_id,
            }
            for t in tasks
        ]

@app.post("/api/tasks")
async def add_task(request: TaskCreateRequest, current_user: User = Depends(get_current_user)):
    """Adds a new task with project context."""
    if request.project_id:
        user_projects = store.get_user_projects(current_user.user_id)
        if request.project_id not in [p.project_id for p in user_projects]:
            raise HTTPException(status_code=403, detail="Access denied to project")

    try:
        task_id = f"{request.name.replace(' ', '_')}_{str(uuid.uuid4())[:8]}"
        
        def dummy_task():
            import time
            import random
            time.sleep(random.uniform(0.5, 2))
            return f"Completed: {request.name}"

        policy = RetryPolicy(max_retries=request.max_retries, base_delay=request.base_delay)
        manager.add_task(
            task_id=task_id,
            func=dummy_task,
            priority=request.priority,
            retry_policy=policy,
            project_id=request.project_id
        )
        
        task = manager.get_task(task_id)
        if task: task.name = request.name

        for dep_id in request.dependencies:
            manager.add_dependency(dep_id, task_id)

        return {"status": "success", "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, current_user: User = Depends(get_current_user)):
    if task_id not in manager.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check access
    task = manager.tasks[task_id]
    if task.project_id:
        user_projects = store.get_user_projects(current_user.user_id)
        if task.project_id not in [p.project_id for p in user_projects]:
            raise HTTPException(status_code=403, detail="Access denied")

    manager.cancel_task(task_id)
    return {"status": "cancelled", "id": task_id}

@app.post("/api/tasks/{task_id}/retry")
async def retry_task(task_id: str, current_user: User = Depends(get_current_user)):
    with manager.lock:
        task = manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.project_id:
            user_projects = store.get_user_projects(current_user.user_id)
            if task.project_id not in [p.project_id for p in user_projects]:
                raise HTTPException(status_code=403, detail="Access denied")

        if task.status not in (TaskStatus.FAILED, TaskStatus.CANCELLED):
            raise HTTPException(status_code=400, detail="Only failed or cancelled tasks can be retried")

        task.status = TaskStatus.PENDING
        task.retries = 0
        task.error = None
        if manager.state_store:
            manager.state_store.save_task(task)

    return {"status": "retrying", "id": task_id}

@app.post("/api/execute")
async def execute_all(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    # Note: This executes ALL tasks, which might span across projects. 
    # In a real multi-tenant system, we'd filter by project.
    background_tasks.add_task(manager.execute_all)
    return {"status": "execution_started"}

# Scheduling Endpoints
@app.post("/api/tasks/{task_id}/schedule")
async def add_schedule(task_id: str, request: Dict[str, str], current_user: User = Depends(get_current_user)):
    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.project_id:
        user_projects = store.get_user_projects(current_user.user_id)
        if task.project_id not in [p.project_id for p in user_projects]:
            raise HTTPException(status_code=403, detail="Access denied")

    schedule_type = request.get("type") # 'cron' or 'interval'
    schedule_value = request.get("value")
    
    if schedule_type not in ["cron", "interval"]:
        raise HTTPException(status_code=400, detail="Invalid schedule type")

    scheduler.add_schedule(task_id, schedule_type, schedule_value)
    return {"status": "scheduled", "task_id": task_id}

@app.get("/api/logs")
async def get_logs(limit: int = 100, current_user: User = Depends(get_current_user)):
    from .logging import StructuredLogger
    # Note: Logs are currently not filtered by project as they are in-memory global buffer
    return {"logs": StructuredLogger.get_buffer()[-limit:]}
