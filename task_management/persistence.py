from abc import ABC, abstractmethod
import sqlite3
import json
from typing import Dict
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
    """SQLite implementation of TaskStateStore.

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
                    data TEXT
                )
            """
            )

    def save_task(self, task: Task):
        """Persists a task's current state as JSON to the SQLite database.

        Args:
            task: The Task instance to save.
        """
        # We exclude 'func' from serialization as it's not JSON serializable and should be re-attached on load
        # However, Task holds 'func'. In a real scenario, you'd store the function path or registry name.
        # For this system, we assume 'func' is provided or restored by the TaskManager.
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (task_id, data) VALUES (?, ?)",
                (task.task_id, task.model_dump_json(exclude={"func", "error"})),
            )

    def load_tasks(self) -> Dict[str, dict]:
        """Loads all tasks from the SQLite database.

        Returns:
            A dictionary mapping task IDs to task data dictionaries.
        """
        tasks = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM tasks")
                for row in cursor:
                    task_data = json.loads(row[0])
                    # Ensure compatibility by casting back to enums and sets
                    task_data["status"] = TaskStatus(task_data["status"])
                    task_data["dependencies"] = set(task_data["dependencies"])
                    task_data["dependents"] = set(task_data["dependents"])
                    tasks[task_data["task_id"]] = task_data
        except sqlite3.OperationalError:
            pass
        return tasks

    def clear(self):
        """Removes all data from the tasks table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tasks")
