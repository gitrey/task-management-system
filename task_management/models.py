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
    """Represents a single task in the system."""

    def __init__(
        self,
        task_id: str,
        func: Optional[Callable],
        priority: int = 0,
        retry_policy: Optional["RetryPolicy"] = None,
    ):
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
        if self.priority == other.priority:
            return self.task_id < other.task_id
        return self.priority < other.priority
