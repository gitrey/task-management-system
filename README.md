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
from task_management import TaskManager, TaskStatus
import time

# Initialize manager with 2 concurrent workers
manager = TaskManager(max_workers=2)

def slow_task():
    print("Starting slow task...")
    time.sleep(1)
    return "Result of A"

def dependent_task():
    task_a = manager.get_task("A")
    print(f"Task B starting after Task A finished with: {task_a.result}")
    return "Result of B"

# Add tasks
manager.add_task("A", slow_task, priority=1)
manager.add_task("B", dependent_task, priority=0)

# Add dependency: B depends on A
manager.add_dependency("A", "B")

# Execute all
print("Executing DAG...")
manager.execute_all()

# Check results
task_b = manager.get_task("B")
print(f"Final State of B: {task_b.status}")
print(f"Result of B: {task_b.result}")
```

## Design Doc: Architecture & Trade-offs

### Concurrency Model: Why `RLock` over `Lock`?

We use `threading.RLock` (Reentrant Lock) instead of a standard `Lock`. This is critical because some internal methods in `TaskManager` (like `_cancel_task_cascade`) are called both from external entry points (which acquire the lock) and recursively from within other locked methods. Using an `RLock` allows the same thread to acquire the lock multiple times without deadlocking itself, simplifying implementation for nested operations like cascading cancellation.

### Persistence Strategy: SQLite

We chose SQLite for task state persistence (`StateStore` interface). SQLite provides ACID compliance and is zero-configuration (file-based), making it ideal for standardizing state across restarts without requiring an external database server. The `SQLiteStateStore` checkpoints task status, results, and retry counts, allowing for recovery after crashes.

### Signal Handling & Graceful Shutdown

The system implements handlers for `SIGINT` (Ctrl+C) and `SIGTERM`. Upon receiving these signals, the `TaskManager` sets a shutdown flag and stops dispatching new tasks. This ensures that active threads have a chance to complete their current unit of work and checkpoint their state before the process terminates.

### Structured Logging

Logging is implemented using JSON formats. This is a production standard as it allows automated log aggregators (like ELK or Datadog) to parse fields (`trace_id`, `task_id`, `event`) without complex regex, facilitating easier debugging in distributed or highly concurrent environments.

## Running Tests

To run the test suite, ensure `pytest` is installed:

```bash
python3 -m pytest test_task_management.py -v
```
