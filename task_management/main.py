import logging
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .manager import TaskManager
from .models import Task, TaskStatus, TaskCreateRequest
from .retry import RetryPolicy
from .persistence import SQLiteStateStore

app = FastAPI(title="Task Management System API")

# Enable CORS for the web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TaskManager with persistence
# Use a common DB file or one specified in environment
store = SQLiteStateStore("tasks.db")
manager = TaskManager(state_store=store)


@app.get("/healthz")
async def healthz():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    """Readiness probe."""
    try:
        if manager.state_store:
            manager.state_store.conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not ready: {str(e)}")


@app.get("/api/tasks", response_model=List[Dict[str, Any]])
async def get_tasks():
    """Returns all tasks in the system."""
    with manager.lock:
        return [
            {
                "id": t.task_id,
                "name": t.name or t.task_id,
                "priority": t.priority,
                "status": t.status.value,
                "dependencies": list(t.dependencies),
                "dependents": list(t.dependents),
                "result": t.result,
                "error": str(t.error) if t.error else None,
                "trace_id": t.trace_id,
            }
            for t in manager.tasks.values()
        ]


@app.post("/api/tasks")
async def add_task(request: TaskCreateRequest):
    """Adds a new task to the manager."""
    try:
        # Generate a unique task_id if name is not unique, but here we'll use name as ID for simplicity
        # matching the UI's expectation of IDs.
        task_id = request.name.replace(" ", "_")

        def dummy_task():
            import time
            import random

            time.sleep(random.uniform(0.5, 2))
            return f"Completed: {request.name}"

        policy = RetryPolicy(
            max_retries=request.max_retries,
            base_delay=request.base_delay,
        )
        manager.add_task(
            task_id=task_id,
            func=dummy_task,
            priority=request.priority,
            retry_policy=policy,
        )
        # Store the name separately in the task model
        task = manager.get_task(task_id)
        if task:
            task.name = request.name

        for dep_id in request.dependencies:
            manager.add_dependency(dep_id, task_id)

        return {"status": "success", "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancels a specific task."""
    if task_id not in manager.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    manager.cancel_task(task_id)
    return {"status": "cancelled", "id": task_id}


@app.post("/api/tasks/{task_id}/retry")
async def retry_task(task_id: str):
    """Manually retries a failed task."""
    with manager.lock:
        task = manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status not in (TaskStatus.FAILED, TaskStatus.CANCELLED):
            raise HTTPException(
                status_code=400, detail="Only failed or cancelled tasks can be retried"
            )

        task.status = TaskStatus.PENDING
        task.retries = 0
        task.error = None
        if manager.state_store:
            manager.state_store.save_task(task)

    return {"status": "retrying", "id": task_id}


@app.post("/api/execute")
async def execute_all(background_tasks: BackgroundTasks):
    """Triggers execution of all tasks."""
    background_tasks.add_task(manager.execute_all)
    return {"status": "execution_started"}


@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """Retrieves the latest logs."""
    from .logging import StructuredLogger

    return {"logs": StructuredLogger.get_buffer()[-limit:]}
