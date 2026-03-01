# Task Management System

A task management system implemented in Python. It supports task prioritization, dependency management in a Directed Acyclic Graph (DAG), and cascading cancellations.

## Features

- **DAG-based Scheduling**: Tasks are executed based on their dependencies.
- **Priority Queue**: Tasks ready for execution are prioritized based on a user-defined priority level.
- **Cycle Detection**: Automatically detects and prevents circular dependencies.
- **Cascaded Cancellation**: If a task fails or is manually cancelled, all dependent tasks are automatically cancelled.
- **Retry Policies**: Configurable exponential backoff for transient failure recovery.
- **State Persistence**: SQLite-based checkpointing allows resuming the DAG after crashes or restarts.
- **Graceful Shutdown**: Handles `SIGINT`/`SIGTERM` signals to allow active tasks to finish and checkpoint.
- **Structured Logging**: JSON-formatted logs with `trace_id` for production observability.
- **Thread-safe**: Utilizes `ThreadPoolExecutor` and `threading.RLock` for safe concurrent execution.
- **Type Safety & Validation**: Leverages Pydantic `BaseModel` for robust task configuration and state management.

## Installation

Ensure you have Python 3.9 or higher installed. Then, install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Project Structure

The project is organized into a modular package structure:

- `task_management/`: Core package directory.
  - `__init__.py`: Public API entry point.
  - `manager.py`: Main `TaskManager` execution logic.
  - `models.py`: Task descriptions, enums, and specific error types.
  - `persistence.py`: State management and SQLite backing.
  - `retry.py`: Exponential backoff and retry policy logic.
  - `logging.py`: Structured JSON logging implementation.
- `test_task_management.py`: Comprehensive test suite.
- `requirements.txt`: Project dependencies.

## Sample Usage

```python
from task_management import TaskManager, TaskStatus, RetryPolicy, SQLiteStateStore
import time

# 1. Initialize with Persistence (optional)
store = SQLiteStateStore("my_tasks.db")
manager = TaskManager(max_workers=2, state_store=store)

# 2. Define a task with a Retry Policy
# This task will retry up to 3 times with exponential backoff if it fails
policy = RetryPolicy(max_retries=3, base_delay=1.0)

def unstable_task():
    print("Executing unstable task...")
    # Simulate transient failure
    if not hasattr(unstable_task, "failed"):
        unstable_task.failed = True
        raise ValueError("Temporary glitch!")
    return "Stable result"

def dependent_task():
    task_a = manager.get_task("A")
    print(f"Task B starting after Task A finished with: {task_a.result}")
    return "Final Output"

# 3. Add tasks and dependencies
manager.add_task("A", unstable_task, retry_policy=policy)
manager.add_task("B", dependent_task)
manager.add_dependency("A", "B")

# 4. Execute all (respects DAG and retries)
print("Executing DAG...")
manager.execute_all()

# 5. Check results (Type-safe access via Pydantic model)
task_b = manager.get_task("B")
if task_b and task_b.status == TaskStatus.COMPLETED:
    print(f"Success! Result: {task_b.result}")
```

## Architecture & Trade-offs

### Concurrency Model: Why `RLock` over `Lock`?

We use `threading.RLock` (Reentrant Lock) instead of a standard `Lock`. This is critical because some internal methods in `TaskManager` (like `_cancel_task_cascade`) are called both from external entry points (which acquire the lock) and recursively from within other locked methods. Using an `RLock` allows the same thread to acquire the lock multiple times without deadlocking itself, simplifying implementation for nested operations like cascading cancellation.

### Persistence Strategy: SQLite

We chose SQLite for task state persistence (`StateStore` interface). SQLite provides ACID compliance and is zero-configuration (file-based), making it ideal for standardizing state across restarts without requiring an external database server. The `SQLiteStateStore` checkpoints task state by serializing Pydantic models to JSON, ensuring data schema integrity and easy recovery after crashes.

### Model Validation: Pydantic

We integrated Pydantic to handle the `Task` and `RetryPolicy` models. This choice replaces manual dictionary-heavy configuration with structured, type-hinted classes that provide automatic validation (e.g., ensuring `max_retries` is non-negative) and simplified (de)serialization for both logging and persistence.

### Signal Handling & Graceful Shutdown

The system implements handlers for `SIGINT` (Ctrl+C) and `SIGTERM`. Upon receiving these signals, the `TaskManager` sets a shutdown flag and stops dispatching new tasks. This ensures that active threads have a chance to complete their current unit of work and checkpoint their state before the process terminates.

### Structured Logging

Logging is implemented using JSON formats. This is a production standard as it allows automated log aggregators (like ELK or Datadog) to parse fields (`trace_id`, `task_id`, `event`) without complex regex, facilitating easier debugging in distributed or highly concurrent environments.

## Running Tests

To run the test suite, ensure `pytest` is installed:

```bash
python3 -m pytest test_task_management.py -v
```
