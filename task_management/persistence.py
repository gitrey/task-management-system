from abc import ABC, abstractmethod
import sqlite3
import json
from typing import Dict, List, Set
from .models import TaskStatus, Task


class StateStore(ABC):
    """Interface for task state persistence."""

    @abstractmethod
    def save_task(self, task: Task):
        """Saves the state of a task.

        Args:
            task: The Task instance to persist.
        """
        pass

    @abstractmethod
    def load_tasks(self) -> Dict[str, dict]:
        """Loads all persisted tasks.

        Returns:
            A dictionary mapping task IDs to their stored attribute dictionaries.
        """
        pass

    @abstractmethod
    def clear(self):
        """Clears all persisted task state."""
        pass


class SQLiteStateStore(StateStore):
    """SQLite implementation of TaskStateStore using a relational schema.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: str = "tasks.db"):
        """Initializes the SQLite state store.

        Args:
            db_path: Path to the SQLite database file. Defaults to "tasks.db".
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'PENDING',
                    retries INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    base_delay REAL DEFAULT 1.0,
                    max_delay REAL DEFAULT 60.0,
                    result TEXT,
                    error TEXT,
                    trace_id TEXT NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id TEXT NOT NULL,
                    depends_on_task_id TEXT NOT NULL,
                    PRIMARY KEY (task_id, depends_on_task_id),
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE
                )
            """
            )

    def save_task(self, task: Task):
        """Persists a task's current state to the SQLite database.

        Args:
            task: The Task instance to save.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Save task attributes
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    task_id, name, priority, status, retries, 
                    max_retries, base_delay, max_delay, result, error, trace_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.task_id,
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

            # Save dependencies
            # First clear existing ones for this task
            conn.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task.task_id,))
            for dep_id in task.dependencies:
                conn.execute(
                    "INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
                    (task.task_id, dep_id),
                )

    def load_tasks(self) -> Dict[str, dict]:
        """Loads all tasks and their dependencies from the SQLite database.

        Returns:
            A dictionary mapping task IDs to task data dictionaries.
        """
        tasks = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM tasks")
                for row in cursor:
                    task_id = row["task_id"]
                    task_data = {
                        "task_id": task_id,
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
                    tasks[task_id] = task_data

                # Load all dependencies
                cursor = conn.execute("SELECT * FROM task_dependencies")
                for row in cursor:
                    t_id = row["task_id"]
                    dep_id = row["depends_on_task_id"]
                    if t_id in tasks:
                        tasks[t_id]["dependencies"].add(dep_id)
                    if dep_id in tasks:
                        tasks[dep_id]["dependents"].add(t_id)
        except sqlite3.OperationalError:
            pass
        return tasks

    def clear(self):
        """Removes all data from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM task_dependencies")
            conn.execute("DELETE FROM tasks")
