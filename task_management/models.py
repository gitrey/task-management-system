import enum
import uuid
from typing import Callable, Any, Set, Optional
from pydantic import BaseModel, ConfigDict, Field


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


class TaskCreateRequest(BaseModel):
    """Request model for creating a new task."""

    name: str = Field(..., min_length=1, max_length=100)
    project_id: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)
    max_retries: int = Field(default=3, ge=0)
    base_delay: float = Field(default=1.0, gt=0)
    dependencies: Set[str] = Field(default_factory=set)


class User(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    hashed_password: str


class Project(BaseModel):
    project_id: str
    name: str
    owner_id: str


class Task(BaseModel):
    """Represents a single task in the system.

    Attributes:
        task_id: Unique identifier for the task.
        project_id: ID of the project this task belongs to.
        name: Human-readable name for the task.
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str
    project_id: Optional[str] = None
    name: Optional[str] = None
    func: Optional[Callable] = None
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Any] = None
    dependencies: Set[str] = Field(default_factory=set)
    dependents: Set[str] = Field(default_factory=set)
    retries: int = 0
    retry_policy: Optional[Any] = (
        None  # Using Any to avoid circular import issues in type hint
    )
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, **data: Any):
        """Initializes a new Task with Pydantic validation."""
        super().__init__(**data)
        if self.retry_policy is None:
            from .retry import RetryPolicy

            self.retry_policy = RetryPolicy(max_retries=0)

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
