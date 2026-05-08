import sqlite3
import json
import os
import contextlib
from typing import Dict, List, Set, Optional
from abc import ABC, abstractmethod

try:
    import psycopg2
    from psycopg2 import pool, extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

from .models import TaskStatus, Task, User, Project


class StateStore(ABC):
    """Interface for task state persistence."""

    @abstractmethod
    def save_task(self, task: Task):
        pass

    @abstractmethod
    def load_tasks(self, project_id: Optional[str] = None) -> Dict[str, dict]:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def save_user(self, user: User):
        pass

    @abstractmethod
    def get_user(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def save_project(self, project: Project):
        pass

    @abstractmethod
    def get_user_projects(self, user_id: str) -> List[Project]:
        pass


class SQLiteStateStore(StateStore):
    """ SQLite implementation of TaskStateStore. """

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self._init_db()

    @property
    def conn(self):
        # We create a new connection per call to be thread-safe in a simple way
        # with SQLite and FastAPI (using background tasks)
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self.conn as conn:
            conn.executescript(open('db/schema.sql').read())

    def save_task(self, task: Task):
        with self.conn as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    task_id, project_id, name, priority, status, retries, 
                    max_retries, base_delay, max_delay, result, error, trace_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.task_id,
                    task.project_id,
                    task.name,
                    task.priority,
                    task.status.value,
                    task.retries,
                    task.retry_policy.max_retries if task.retry_policy else 0,
                    task.retry_policy.base_delay if task.retry_policy else 1.0,
                    task.retry_policy.max_delay if task.retry_policy else 60.0,
                    json.dumps(task.result) if task.result is not None else None,
                    str(task.error) if task.error else None,
                    task.trace_id,
                ),
            )
            conn.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task.task_id,))
            for dep_id in task.dependencies:
                conn.execute(
                    "INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
                    (task.task_id, dep_id),
                )

    def load_tasks(self, project_id: Optional[str] = None) -> Dict[str, dict]:
        tasks = {}
        query = "SELECT * FROM tasks"
        params = []
        if project_id:
            query += " WHERE project_id = ?"
            params.append(project_id)
            
        with self.conn as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            for row in cursor:
                task_id = row["task_id"]
                tasks[task_id] = {
                    "task_id": task_id,
                    "project_id": row["project_id"],
                    "name": row["name"],
                    "priority": row["priority"],
                    "status": TaskStatus(row["status"]),
                    "retries": row["retries"],
                    "result": json.loads(row["result"]) if row["result"] else None,
                    "error": row["error"],
                    "trace_id": row["trace_id"],
                    "dependencies": set(),
                    "dependents": set(),
                    "retry_policy": {
                        "max_retries": row["max_retries"],
                        "base_delay": row["base_delay"],
                        "max_delay": row["max_delay"],
                    },
                }
            cursor = conn.execute("SELECT * FROM task_dependencies")
            for row in cursor:
                t_id, dep_id = row["task_id"], row["depends_on_task_id"]
                if t_id in tasks: tasks[t_id]["dependencies"].add(dep_id)
                if dep_id in tasks: tasks[dep_id]["dependents"].add(t_id)
        return tasks

    def clear(self):
        with self.conn as conn:
            conn.execute("DELETE FROM task_dependencies")
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM users")
            conn.execute("DELETE FROM projects")
            conn.execute("DELETE FROM project_members")

    def save_user(self, user: User):
        with self.conn as conn:
            conn.execute(
                "INSERT OR REPLACE INTO users (user_id, username, hashed_password, email) VALUES (?, ?, ?, ?)",
                (user.user_id, user.username, user.hashed_password, user.email)
            )

    def get_user(self, username: str) -> Optional[User]:
        with self.conn as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return User(**dict(row))
        return None

    def save_project(self, project: Project):
        with self.conn as conn:
            conn.execute(
                "INSERT OR REPLACE INTO projects (project_id, name, owner_id) VALUES (?, ?, ?)",
                (project.project_id, project.name, project.owner_id)
            )
            conn.execute(
                "INSERT OR IGNORE INTO project_members (project_id, user_id) VALUES (?, ?)",
                (project.project_id, project.owner_id)
            )

    def get_user_projects(self, user_id: str) -> List[Project]:
        projects = []
        with self.conn as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT p.* FROM projects p JOIN project_members pm ON p.project_id = pm.project_id WHERE pm.user_id = ?",
                (user_id,)
            )
            for row in cursor:
                projects.append(Project(**dict(row)))
        return projects


class PostgreSQLStateStore(StateStore):
    """PostgreSQL implementation of TaskStateStore using connection pooling."""

    def __init__(self, dsn: str, min_conn: int = 1, max_conn: int = 10):
        if not HAS_POSTGRES:
            raise ImportError("psycopg2-binary is required for PostgreSQL support")
        self.dsn = dsn
        self.pool = pool.ThreadedConnectionPool(min_conn, max_conn, dsn)
        # We don't automatically init schema here as it might require complex migrations
        # But we verify connectivity
        with self.connection() as conn:
            pass

    @contextlib.contextmanager
    def connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)

    def save_task(self, task: Task):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tasks (
                        task_id, project_id, name, priority, status, retries, 
                        max_retries, base_delay, max_delay, result, error, trace_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (task_id) DO UPDATE SET
                        project_id = EXCLUDED.project_id,
                        name = EXCLUDED.name,
                        priority = EXCLUDED.priority,
                        status = EXCLUDED.status,
                        retries = EXCLUDED.retries,
                        max_retries = EXCLUDED.max_retries,
                        base_delay = EXCLUDED.base_delay,
                        max_delay = EXCLUDED.max_delay,
                        result = EXCLUDED.result,
                        error = EXCLUDED.error,
                        trace_id = EXCLUDED.trace_id
                """,
                    (
                        task.task_id,
                        task.project_id,
                        task.name,
                        task.priority,
                        task.status.value,
                        task.retries,
                        task.retry_policy.max_retries if task.retry_policy else 0,
                        task.retry_policy.base_delay if task.retry_policy else 1.0,
                        task.retry_policy.max_delay if task.retry_policy else 60.0,
                        json.dumps(task.result) if task.result is not None else None,
                        str(task.error) if task.error else None,
                        task.trace_id,
                    ),
                )
                cur.execute("DELETE FROM task_dependencies WHERE task_id = %s", (task.task_id,))
                for dep_id in task.dependencies:
                    cur.execute(
                        "INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES (%s, %s)",
                        (task.task_id, dep_id),
                    )

    def load_tasks(self, project_id: Optional[str] = None) -> Dict[str, dict]:
        tasks = {}
        query = "SELECT * FROM tasks"
        params = []
        if project_id:
            query += " WHERE project_id = %s"
            params.append(project_id)

        with self.connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, params)
                for row in cur:
                    task_id = row["task_id"]
                    tasks[task_id] = {
                        "task_id": task_id,
                        "project_id": row["project_id"],
                        "name": row["name"],
                        "priority": row["priority"],
                        "status": TaskStatus(row["status"]),
                        "retries": row["retries"],
                        "result": json.loads(row["result"]) if row["result"] else None,
                        "error": row["error"],
                        "trace_id": row["trace_id"],
                        "dependencies": set(),
                        "dependents": set(),
                        "retry_policy": {
                            "max_retries": row["max_retries"],
                            "base_delay": row["base_delay"],
                            "max_delay": row["max_delay"],
                        },
                    }
                cur.execute("SELECT * FROM task_dependencies")
                for row in cur:
                    t_id, dep_id = row["task_id"], row["depends_on_task_id"]
                    if t_id in tasks:
                        tasks[t_id]["dependencies"].add(dep_id)
                    if dep_id in tasks:
                        tasks[dep_id]["dependents"].add(t_id)
        return tasks

    def clear(self):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE task_dependencies CASCADE")
                cur.execute("TRUNCATE TABLE tasks CASCADE")
                cur.execute("TRUNCATE TABLE users CASCADE")
                cur.execute("TRUNCATE TABLE projects CASCADE")
                cur.execute("TRUNCATE TABLE project_members CASCADE")

    def save_user(self, user: User):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (user_id, username, hashed_password, email) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        hashed_password = EXCLUDED.hashed_password,
                        email = EXCLUDED.email
                """,
                    (user.user_id, user.username, user.hashed_password, user.email),
                )

    def get_user(self, username: str) -> Optional[User]:
        with self.connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
                if row:
                    return User(**dict(row))
        return None

    def save_project(self, project: Project):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO projects (project_id, name, owner_id) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (project_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        owner_id = EXCLUDED.owner_id
                """,
                    (project.project_id, project.name, project.owner_id),
                )
                cur.execute(
                    "INSERT INTO project_members (project_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (project.project_id, project.owner_id),
                )

    def get_user_projects(self, user_id: str) -> List[Project]:
        projects = []
        with self.connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT p.* FROM projects p JOIN project_members pm ON p.project_id = pm.project_id WHERE pm.user_id = %s",
                    (user_id,),
                )
                for row in cur:
                    projects.append(Project(**dict(row)))
        return projects
