"""Task Management System with DAG, Priorities, and Cascading Cancellation.

This module provides a robust TaskManager for executing tasks according to a
Directed Acyclic Graph (DAG). It supports task prioritization, circular
dependency detection, and automatic cascading cancellation of dependent tasks
upon failure or manual cancellation.
"""

import enum
import threading
import heapq
import time
from typing import Callable, Any, Dict, List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, Future


class TaskStatus(enum.Enum):
    """Enumeration of possible task states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskCycleError(Exception):
    """Raised when a circular dependency is detected."""

    pass


class Task:
    """Represents a single task in the system.

    Attributes:
        task_id: Unique identifier for the task.
        func: The callable to be executed.
        priority: Task priority (lower value means higher priority).
        status: Current status of the task.
        result: Result returned by the task function if successful.
        error: Exception caught during execution if failed.
        dependencies: Set of task IDs that this task depends on.
        dependents: Set of task IDs that depend on this task.
    """

    def __init__(self, task_id: str, func: Callable, priority: int = 0):
        """Initializes a Task instance.

        Args:
            task_id: Unique identifier for the task.
            func: The callable to be executed.
            priority: Task priority (default: 0).
        """
        self.task_id = task_id
        self.func = func
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[Exception] = None
        self.dependencies: Set[str] = set()
        self.dependents: Set[str] = set()

    def __lt__(self, other: "Task") -> bool:
        """Comparison for priority queue (heapq).

        Args:
            other: The other task to compare against.

        Returns:
            True if this task has higher priority (lower value) than the other.
        """
        if self.priority == other.priority:
            return self.task_id < other.task_id
        return self.priority < other.priority


class TaskManager:
    """Manager for scheduling and executing tasks with dependencies.

    Handles a Directed Acyclic Graph (DAG) of tasks, ensuring they execute in
    correct order based on dependencies and priorities. Supports cascading
    cancellation on failure or manual request.

    Args:
        max_workers: Maximum number of concurrent tasks (default: 4).
    """

    def __init__(self, max_workers: int = 4):
        self.tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.lock = threading.RLock()
        self._condition = threading.Condition(self.lock)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.futures: Dict[str, Future] = {}
        self._is_running = False

    def add_task(self, task_id: str, func: Callable, priority: int = 0) -> None:
        """Adds a new task to the manager.

        Args:
            task_id: Unique identifier for the task.
            func: The function to execute.
            priority: Priority level (lower is higher priority).

        Raises:
            ValueError: If task_id already exists.
        """
        with self.lock:
            if task_id in self.tasks:
                raise ValueError(f"Task {task_id} already exists")
            self.tasks[task_id] = Task(task_id, func, priority)

    def add_dependency(self, from_task_id: str, to_task_id: str) -> None:
        """Defines a dependency between two tasks.

        Args:
            from_task_id: The task that must complete first.
            to_task_id: The task that depends on from_task_id.

        Raises:
            ValueError: If either task ID does not exist.
            TaskCycleError: If adding the dependency would create a cycle.
        """
        with self.lock:
            if from_task_id not in self.tasks or to_task_id not in self.tasks:
                raise ValueError("Both tasks must exist before adding a dependency")

            if self._will_create_cycle(from_task_id, to_task_id):
                raise TaskCycleError(
                    f"Adding dependency {from_task_id} -> {to_task_id} creates a cycle"
                )

            self.tasks[to_task_id].dependencies.add(from_task_id)
            self.tasks[from_task_id].dependents.add(to_task_id)

    def _will_create_cycle(self, from_id: str, to_id: str) -> bool:
        """Checks if adding an edge from from_id to to_id creates a cycle.

        Args:
            from_id: Source task ID.
            to_id: Target task ID.

        Returns:
            True if a cycle would be created, False otherwise.
        """
        visited = set()
        stack = [to_id]
        while stack:
            curr = stack.pop()
            if curr == from_id:
                return True
            if curr not in visited:
                visited.add(curr)
                stack.extend(self.tasks[curr].dependents - visited)
        return False

    def cancel_task(self, task_id: str) -> None:
        """Cancels a task and all its recursive dependents.

        Args:
            task_id: The task ID to cancel.
        """
        with self.lock:
            self._cancel_task_cascade(task_id, cascade=True)
            self._condition.notify_all()

    def _cancel_task_cascade(self, task_id: str, cascade: bool = True) -> None:
        """Internal helper for cascading task cancellation.

        Args:
            task_id: The task ID to cancel.
            cascade: Whether to recursively cancel dependents.
        """
        task = self.tasks.get(task_id)
        if not task or task.status in (
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
            TaskStatus.FAILED,
        ):
            return

        task.status = TaskStatus.CANCELLED
        if task_id in self.futures:
            self.futures[task_id].cancel()

        if cascade:
            for dep_id in list(task.dependents):
                self._cancel_task_cascade(dep_id, cascade=True)

    def _get_ready_tasks(self) -> List[Task]:
        """Identifies tasks whose dependencies are met and are ready to run.

        Returns:
            A list of Tasks sorted by priority.
        """
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                all_completed = True
                for dep_id in task.dependencies:
                    if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                        all_completed = False
                        break

                if all_completed:
                    ready.append(task)

        heapq.heapify(ready)
        result = []
        while ready:
            result.append(heapq.heappop(ready))
        return result

    def _task_wrapper(self, task_id: str) -> None:
        """Wrapper to execute the task function and handle state transitions.

        Args:
            task_id: The ID of the task to run.
        """
        with self.lock:
            task = self.tasks[task_id]
            if task.status != TaskStatus.RUNNING:
                return

        try:
            res = task.func()
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.result = res
        except Exception as e:
            with self.lock:
                task.status = TaskStatus.FAILED
                task.error = e
                for dep_id in list(task.dependents):
                    self._cancel_task_cascade(dep_id, cascade=True)
        finally:
            with self.lock:
                self._condition.notify_all()

    def execute_all(self, timeout: Optional[float] = None) -> None:
        """Starts task execution and blocks until all tasks reach terminal state.

        Args:
            timeout: Optional time limit for entire execution in seconds.
        """
        self._is_running = True
        start_time = time.time()

        with self.lock:
            while self._is_running:
                terminal_states = {
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED,
                }
                all_terminal = all(
                    t.status in terminal_states for t in self.tasks.values()
                )
                if all_terminal:
                    break

                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        break

                ready_tasks = self._get_ready_tasks()
                for task in ready_tasks:
                    task.status = TaskStatus.RUNNING
                    future = self.executor.submit(self._task_wrapper, task.task_id)
                    self.futures[task.task_id] = future

                wait_time = (
                    max(0.1, (timeout - (time.time() - start_time)))
                    if timeout
                    else None
                )
                self._condition.wait(
                    timeout=wait_time if timeout and wait_time < 1.0 else 1.0
                )

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieves a task from the manager.

        Args:
            task_id: Unique identifier for the task.

        Returns:
            The Task object if found, else None.
        """
        with self.lock:
            return self.tasks.get(task_id)

    def shutdown(self, wait: bool = True) -> None:
        """Shuts down the thread pool executor.

        Args:
            wait: Whether to wait for running tasks to complete.
        """
        self._is_running = False
        self.executor.shutdown(wait=wait)
