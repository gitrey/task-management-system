import enum
import uuid
from typing import Callable, Any, Set, Optional


class TaskStatus(enum.Enum):
    """Enumeration of possible task states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"


class TaskCycleError(Exception):
    """Raised when a circular dependency is detected."""

    pass


class Task:
    """Represents a single task in the system.

    Attributes:
        task_id: Unique identifier for the task.
        func: The callable to be executed.
        priority: Numerical priority (lower is higher priority).
        status: Current state of the task.
        result: Return value of the task after successful execution.
        error: Caught exception if the task failed.
        dependencies: Set of task IDs that this task depends on.
        dependents: Set of task IDs that depend on this task.
        retries: Number of retry attempts made so far.
        retry_policy: Configuration for retry behavior.
        trace_id: Unique UUID for tracing the task execution.
    """

    def __init__(
        self,
        task_id: str,
        func: Optional[Callable],
        priority: int = 0,
        retry_policy: Optional["RetryPolicy"] = None,
    ):
        """Initializes a new Task.

        Args:
            task_id: Unique identifier for the task.
            func: The callable to be executed.
            priority: Numerical priority (lower is higher priority). Defaults to 0.
            retry_policy: Retry configuration. Defaults to no retries.
        """
        from .retry import RetryPolicy  # Deferred import to avoid circular dependency

        self.task_id = task_id
        self.func = func
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[Exception] = None
        self.dependencies: Set[str] = set()
        self.dependents: Set[str] = set()
        self.retries = 0
        self.retry_policy = retry_policy or RetryPolicy(max_retries=0)
        self.trace_id = str(uuid.uuid4())

    def __lt__(self, other: "Task") -> bool:
        """Determines priority ordering between two tasks.

        Args:
            other: The other task to compare against.

        Returns:
            True if this task has higher priority (lower priority number).
        """
        if self.priority == other.priority:
            return self.task_id < other.task_id
        return self.priority < other.priority
