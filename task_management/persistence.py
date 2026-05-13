from abc import ABC, abstractmethod
import sqlite3
import json
import queue
import threading
from typing import Dict, List
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
    def save_tasks(self, tasks: List[Task]):
        """Saves the state of multiple tasks in a single transaction."""
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

    @abstractmethod
    def flush(self):
        """Blocks until all asynchronous persistence operations are complete."""
        pass

    @abstractmethod
    def stop(self):
        """Cleanly stops the persistence worker."""
        pass


class SQLiteStateStore(StateStore):
    """SQLite implementation of TaskStateStore.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: str = "tasks.db", pool_size: int = 5):
        """Initializes the SQLite state store.

        Args:
            db_path: Path to the SQLite database file. Defaults to "tasks.db".
            pool_size: The number of connections to pool.
        """
        self.db_path = db_path
        self.pool = queue.Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self.pool.put(conn)
            
        self._init_db()
        
        self.save_queue = queue.Queue()
        self._running = True
        self.worker_thread = threading.Thread(target=self._persistence_worker, daemon=True)
        self.worker_thread.start()

    def _init_db(self):
        """Initializes the database schema if it doesn't exist."""
        conn = self.pool.get()
        try:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id TEXT PRIMARY KEY,
                        data TEXT
                    )
                """
                )
        finally:
            self.pool.put(conn)

    def _persistence_worker(self):
        conn = self.pool.get()
        try:
            while self._running:
                try:
                    batch = self.save_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                    
                if batch is None:
                    self.save_queue.task_done()
                    break
                    
                try:
                    with conn:
                        for task_id, data in batch:
                            conn.execute(
                                "INSERT OR REPLACE INTO tasks (task_id, data) VALUES (?, ?)",
                                (task_id, data),
                            )
                except Exception:
                    pass
                finally:
                    self.save_queue.task_done()
        finally:
            self.pool.put(conn)

    def save_task(self, task: Task):
        """Persists a task's current state as JSON to the SQLite database.

        Args:
            task: The Task instance to save.
        """
        data = task.model_dump_json(exclude={"func", "error"})
        self.save_queue.put([(task.task_id, data)])

    def save_tasks(self, tasks: List[Task]):
        if not tasks:
            return
        batch = [(t.task_id, t.model_dump_json(exclude={"func", "error"})) for t in tasks]
        self.save_queue.put(batch)

    def load_tasks(self) -> Dict[str, dict]:
        """Loads all tasks from the SQLite database.

        Returns:
            A dictionary mapping task IDs to task data dictionaries.
        """
        tasks = {}
        conn = self.pool.get()
        try:
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
        finally:
            self.pool.put(conn)
        return tasks

    def clear(self):
        """Removes all data from the tasks table."""
        conn = self.pool.get()
        try:
            with conn:
                conn.execute("DELETE FROM tasks")
        finally:
            self.pool.put(conn)

    def flush(self):
        self.save_queue.join()
        
    def stop(self):
        self._running = False
        self.save_queue.put(None)
        self.worker_thread.join()
