import pytest
import time
import threading
import os
import json
import logging
from task_management import (
    TaskManager,
    TaskStatus,
    TaskCycleError,
    RetryPolicy,
    SQLiteStateStore,
)


def test_basic_execution():
    manager = TaskManager(max_workers=2)
    results = []

    def my_task():
        results.append(1)
        return "done"

    manager.add_task("A", my_task)
    manager.execute_all()

    task_a = manager.tasks["A"]
    assert task_a.status == TaskStatus.COMPLETED
    assert task_a.result == "done"
    assert results == [1]


def test_dependency_execution():
    manager = TaskManager(max_workers=2)
    execution_order = []

    def task_a():
        time.sleep(0.1)
        execution_order.append("A")

    def task_b():
        execution_order.append("B")

    def task_c():
        execution_order.append("C")

    manager.add_task("B", task_b)
    manager.add_task("A", task_a)
    manager.add_task("C", task_c)

    manager.add_dependency("A", "C")
    manager.add_dependency("A", "B")
    manager.add_dependency("B", "C")

    manager.execute_all()

    assert execution_order == ["A", "B", "C"]


def test_retry_policy():
    manager = TaskManager(max_workers=1)
    attempts = 0

    def resilient_task():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Transient error")
        return "Success"

    policy = RetryPolicy(max_retries=3, base_delay=0.1)
    manager.add_task("R", resilient_task, retry_policy=policy)
    manager.execute_all()

    task = manager.tasks["R"]
    assert task.status == TaskStatus.COMPLETED
    assert task.retries == 2
    assert attempts == 3


def test_persistence(tmp_path):
    db_file = str(tmp_path / "test_tasks.db")
    store = SQLiteStateStore(db_file)
    manager = TaskManager(state_store=store)

    manager.add_task("P1", lambda: "Result 1")
    manager.execute_all()

    # Simulate restart by loading from same store
    tasks_data = store.load_tasks()
    assert "P1" in tasks_data
    assert tasks_data["P1"]["status"] == TaskStatus.COMPLETED
    assert tasks_data["P1"]["result"] == "Result 1"


def test_cascading_failure():
    manager = TaskManager()

    def failing_task():
        raise ValueError("I failed")

    manager.add_task("A", failing_task)
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    manager.execute_all()

    assert manager.tasks["A"].status == TaskStatus.FAILED
    assert manager.tasks["B"].status == TaskStatus.CANCELLED


def test_structured_logging(caplog):
    manager = TaskManager()
    with caplog.at_level(logging.INFO):
        manager.add_task("L", lambda: "Log me")
        manager.execute_all()

    logs = [
        json.loads(record.message)
        for record in caplog.records
        if "TaskManager" in record.name
    ]

    events = [log["event"] for log in logs]
    assert "Task added" in events
    assert "Executing task" in events
    assert "Task completed" in events
    assert all("trace_id" in log for log in logs)


def test_cycle_detection():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    with pytest.raises(TaskCycleError):
        manager.add_dependency("B", "A")
