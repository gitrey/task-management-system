# Task Management System

A production-quality task management system implemented in Python. It supports task prioritization, dependency management in a Directed Acyclic Graph (DAG), and cascading cancellations.

## Features

- **DAG-based Scheduling**: Tasks are executed based on their dependencies.
- **Priority Queue**: Tasks ready for execution are prioritized based on a user-defined priority level.
- **Cycle Detection**: Automatically detects and prevents circular dependencies.
- **Cascading Cancellation**: If a task fails or is manually cancelled, all dependent tasks are automatically cancelled.
- **Thread-safe**: Utilizes `ThreadPoolExecutor` and `threading.RLock` for safe concurrent execution.

## Installation

Ensure you have Python 3.9 or higher installed.

```bash
python3 -m pip install -e .
```

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

## Running Tests

To run the test suite, ensure `pytest` is installed:

```bash
python3 -m pytest test_task_management.py -v
```
