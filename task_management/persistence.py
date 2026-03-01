from abc import ABC, abstractmethod
import sqlite3
import json
from typing import Dict
from .models import TaskStatus, Task


class StateStore(ABC):
    """Interface for task state persistence."""

    @abstractmethod
    def save_task(self, task: Task):
        pass

    @abstractmethod
    def load_tasks(self) -> Dict[str, dict]:
        pass

    @abstractmethod
    def clear(self):
        pass


class SQLiteStateStore(StateStore):
    """SQLite implementation of TaskStateStore."""

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT,
                    priority INTEGER,
                    dependencies TEXT,
                    dependents TEXT,
                    result TEXT,
                    retries INTEGER
                )
            """
            )

    def save_task(self, task: Task):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (task_id, status, priority, dependencies, dependents, result, retries)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.task_id,
                    task.status.value,
                    task.priority,
                    json.dumps(list(task.dependencies)),
                    json.dumps(list(task.dependents)),
                    json.dumps(task.result) if task.result else None,
                    task.retries,
                ),
            )

    def load_tasks(self) -> Dict[str, dict]:
        tasks = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM tasks")
                for row in cursor:
                    tasks[row[0]] = {
                        "status": TaskStatus(row[1]),
                        "priority": row[2],
                        "dependencies": set(json.loads(row[3])),
                        "dependents": set(json.loads(row[4])),
                        "result": json.loads(row[5]) if row[5] else None,
                        "retries": row[6],
                    }
        except sqlite3.OperationalError:
            pass
        return tasks

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tasks")
