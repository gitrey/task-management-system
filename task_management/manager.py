import threading
import heapq
import time
import logging
import signal
from typing import Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, Future

from .models import TaskStatus, Task, TaskCycleError
from .logging import StructuredLogger
from .persistence import StateStore
from .retry import RetryPolicy


class TaskManager:
    """Manager for scheduling and executing tasks with enhancements.

    Attributes:
        tasks: Dictionary of task IDs to Task objects.
        max_workers: Maximum number of concurrent threads.
        lock: Reentrant lock for thread safety.
        executor: ThreadPoolExecutor for task execution.
        futures: Mapping of task IDs to their running futures.
        logger: Structured logger instance.
        state_store: Optional persistent storage for task states.
    """

    def __init__(self, max_workers: int = 4, state_store: Optional[StateStore] = None):
        """Initializes the TaskManager.

        Args:
            max_workers: Maximum number of worker threads. Defaults to 4.
            state_store: Optional StateStore implementation for persistence.
        """
        self.tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.lock = threading.RLock()
        self._condition = threading.Condition(self.lock)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.futures: Dict[str, Future] = {}
        self._is_running = False
        self.logger = StructuredLogger()
        self.state_store = state_store
        self._shutdown_requested = False

        # Graceful shutdown signals
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        """Internal signal handler for graceful shutdown.

        Args:
            signum: The signal number received.
            frame: The current stack frame.
        """
        self.logger.log(
            logging.WARNING,
            "Signal received, initiating graceful shutdown",
            signal=signum,
        )
        self._shutdown_requested = True
        self._is_running = False
        with self.lock:
            self._condition.notify_all()

    def add_task(
        self,
        task_id: str,
        func: Callable,
        priority: int = 0,
        retry_policy: Optional[RetryPolicy] = None,
    ) -> None:
        """Adds a new task to the system.

        Args:
            task_id: Unique identifier for the task.
            func: The callable to be executed.
            priority: Numerical priority (lower is higher priority). Defaults to 0.
            retry_policy: Optional retry configuration.

        Raises:
            ValueError: If a task with the same ID already exists.
        """
        with self.lock:
            if task_id in self.tasks:
                raise ValueError(f"Task {task_id} already exists")
            task = Task(task_id, func, priority, retry_policy)
            self.tasks[task_id] = task
            if self.state_store:
                self.state_store.save_task(task)
            self.logger.log(
                logging.INFO,
                "Task added",
                task_id=task_id,
                priority=priority,
                trace_id=task.trace_id,
            )

    def add_dependency(self, from_task_id: str, to_task_id: str) -> None:
        """Adds a dependency relationship between two tasks.

        Args:
            from_task_id: The task ID that must complete first.
            to_task_id: The task ID that depends on the completion of from_task_id.

        Raises:
            ValueError: If either task ID does not exist.
            TaskCycleError: If the dependency would create a circular reference.
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
            if self.state_store:
                self.state_store.save_task(self.tasks[to_task_id])
                self.state_store.save_task(self.tasks[from_task_id])
            self.logger.log(
                logging.INFO, "Dependency added", from_id=from_task_id, to_id=to_task_id
            )

    def _will_create_cycle(self, from_id: str, to_id: str) -> bool:
        """Checks if adding a dependency would create a cycle.

        Args:
            from_id: ID of the dependency.
            to_id: ID of the dependent task.

        Returns:
            True if a cycle would be created, else False.
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

    def cancel_task(self, task_id: str):
        """Manually cancels a task and cascades to its dependents.

        Args:
            task_id: The unique identifier of the task to cancel.
        """
        with self.lock:
            self._cancel_task_cascade(task_id)
            self._condition.notify_all()

    def _cancel_task_cascade(self, task_id: str):
        """Recursively cancels a task and all tasks that depend on it.

        Args:
            task_id: The unique identifier of the task to cancel.
        """
        task = self.tasks.get(task_id)
        if not task or task.status in (
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
            TaskStatus.FAILED,
        ):
            return

        task.status = TaskStatus.CANCELLED
        if self.state_store:
            self.state_store.save_task(task)
        if task_id in self.futures:
            self.futures[task_id].cancel()

        self.logger.log(
            logging.INFO, "Task cancelled", task_id=task_id, trace_id=task.trace_id
        )

        for dep_id in list(task.dependents):
            self._cancel_task_cascade(dep_id)

    def _get_ready_tasks(self) -> List[Task]:
        """Identifies tasks whose dependencies are met and are ready to run.

        Returns:
            A prioritized list of ready Tasks.
        """
        ready = []
        for task in self.tasks.values():
            if task.status in (TaskStatus.PENDING, TaskStatus.RETRYING):
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

    def _task_wrapper(self, task_id: str):
        """Worker wrapper around task execution.

        Handles retries, logging, and status updates.

        Args:
            task_id: The unique identifier of the task to execute.
        """
        with self.lock:
            task = self.tasks[task_id]
            if task.status != TaskStatus.RUNNING:
                return

        self.logger.log(
            logging.INFO, "Executing task", task_id=task_id, trace_id=task.trace_id
        )
        try:
            res = task.func()
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.result = res
                if self.state_store:
                    self.state_store.save_task(task)
            self.logger.log(
                logging.INFO, "Task completed", task_id=task_id, trace_id=task.trace_id
            )
        except Exception as e:
            with self.lock:
                task.error = e
                if task.retries < task.retry_policy.max_retries:
                    task.retries += 1
                    task.status = TaskStatus.RETRYING
                    delay = task.retry_policy.get_delay(task.retries)
                    self.logger.log(
                        logging.WARNING,
                        "Task failed, retrying",
                        task_id=task_id,
                        retry=task.retries,
                        delay=delay,
                        trace_id=task.trace_id,
                        error=str(e),
                    )
                    threading.Timer(delay, self._mark_ready, args=[task_id]).start()
                else:
                    task.status = TaskStatus.FAILED
                    self.logger.log(
                        logging.ERROR,
                        "Task failed permanently",
                        task_id=task_id,
                        trace_id=task.trace_id,
                        error=str(e),
                    )
                    for dep_id in list(task.dependents):
                        self._cancel_task_cascade(dep_id)
                if self.state_store:
                    self.state_store.save_task(task)
        finally:
            with self.lock:
                self._condition.notify_all()

    def _mark_ready(self, task_id: str):
        """Timer callback to wake up the manager for a retrying task.

        Args:
            task_id: The unique identifier of the task now ready for retry.
        """
        with self.lock:
            if self.tasks[task_id].status == TaskStatus.RETRYING:
                self._condition.notify_all()

    def execute_all(self, timeout: Optional[float] = None):
        """Executes all tasks in the DAG concurrently while respecting dependencies.

        Args:
            timeout: Optional maximum time in seconds to run. Defaults to None (wait indefinitely).
        """
        self._is_running = True
        start_time = time.time()

        with self.lock:
            while self._is_running and not self._shutdown_requested:
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

                if timeout is not None and (time.time() - start_time) >= timeout:
                    break

                ready_tasks = self._get_ready_tasks()
                for task in ready_tasks:
                    task.status = TaskStatus.RUNNING
                    self.futures[task.task_id] = self.executor.submit(
                        self._task_wrapper, task.task_id
                    )

                self._condition.wait(timeout=1.0)

        if self._shutdown_requested:
            self.logger.log(logging.INFO, "Shutdown sequence complete")

    def shutdown(self, wait: bool = True):
        """Signals the manager to stop and shuts down the executor.

        Args:
            wait: Whether to wait for active tasks to finish. Defaults to True.
        """
        self._is_running = False
        self.executor.shutdown(wait=wait)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieves a task from the manager.

        Args:
            task_id: Unique identifier for the task.

        Returns:
            The Task object if found, else None.
        """
        with self.lock:
            return self.tasks.get(task_id)
