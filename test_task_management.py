import pytest
import time
import threading
import os
import json
import logging
import signal
import sqlite3
from task_management import (
    TaskManager,
    TaskStatus,
    TaskCycleError,
    RetryPolicy,
    SQLiteStateStore,
    export_task_hierarchy,
)
from task_management.models import Task


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


def test_pydantic_validation():
    from pydantic import ValidationError

    # Verify RetryPolicy validation
    with pytest.raises(ValidationError):
        RetryPolicy(max_retries=-1)

    with pytest.raises(ValidationError):
        RetryPolicy(base_delay=0)


# Additional tests for coverage increase

def test_add_task_already_exists():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    with pytest.raises(ValueError, match="Task A already exists"):
        manager.add_task("A", lambda: None)


def test_add_dependency_missing_tasks():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    with pytest.raises(ValueError, match="Both tasks must exist"):
        manager.add_dependency("A", "B")


def test_task_comparison():
    t1 = Task(task_id="A", func=lambda: None, priority=1)
    t2 = Task(task_id="B", func=lambda: None, priority=2)
    t3 = Task(task_id="C", func=lambda: None, priority=1)

    assert t1 < t2
    assert t1 < t3  # priority same, "A" < "C"
    assert not (t2 < t1)


def test_sqlite_state_store_clear(tmp_path):
    db_file = str(tmp_path / "test_clear.db")
    store = SQLiteStateStore(db_file)
    task = Task(task_id="T1", func=lambda: None)
    store.save_task(task)
    assert len(store.load_tasks()) == 1
    store.clear()
    assert len(store.load_tasks()) == 0


def test_manager_with_state_store_dependency(tmp_path):
    db_file = str(tmp_path / "test_dep.db")
    store = SQLiteStateStore(db_file)
    manager = TaskManager(state_store=store)
    manager.add_task("A", lambda: None)
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    tasks = store.load_tasks()
    assert "A" in tasks
    assert "B" in tasks
    assert "A" in tasks["B"]["dependencies"]
    assert "B" in tasks["A"]["dependents"]


def test_cancel_task_manual():
    manager = TaskManager()
    manager.add_task("A", lambda: time.sleep(1))
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    manager.cancel_task("A")
    assert manager.get_task("A").status == TaskStatus.CANCELLED
    assert manager.get_task("B").status == TaskStatus.CANCELLED


def test_cancel_already_finished():
    manager = TaskManager()
    manager.add_task("A", lambda: "done")
    manager.execute_all()
    assert manager.get_task("A").status == TaskStatus.COMPLETED

    manager.cancel_task("A")  # should return early
    assert manager.get_task("A").status == TaskStatus.COMPLETED


def test_execute_all_timeout():
    manager = TaskManager()
    manager.add_task("A", lambda: time.sleep(2))
    start = time.time()
    # Use a small timeout. It might take up to 1.0s due to condition.wait(1.0)
    manager.execute_all(timeout=0.2)
    duration = time.time() - start
    assert 0.2 <= duration < 1.5
    manager.shutdown(wait=False)


def test_get_task_missing():
    manager = TaskManager()
    assert manager.get_task("NONEXISTENT") is None


def test_signal_handling():
    manager = TaskManager()
    # Mock _handle_signal call as if it was triggered by a signal
    manager._handle_signal(signal.SIGINT, None)
    assert manager._shutdown_requested == True
    assert manager._is_running == False


def test_retry_permanent_failure_with_dependents_and_state_store(tmp_path):
    db_file = str(tmp_path / "test_fail_state.db")
    store = SQLiteStateStore(db_file)
    manager = TaskManager(state_store=store)

    def failing():
        raise ValueError("Permanent")

    manager.add_task(
        "A", failing, retry_policy=RetryPolicy(max_retries=1, base_delay=0.1)
    )
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    manager.execute_all()
    assert manager.get_task("A").status == TaskStatus.FAILED
    assert manager.get_task("B").status == TaskStatus.CANCELLED

    # Verify it was saved to state store
    tasks = store.load_tasks()
    assert tasks["A"]["status"] == TaskStatus.FAILED


def test_empty_task_list():
    manager = TaskManager()
    manager.execute_all()  # Should just return


def test_task_wrapper_not_running():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    task = manager.get_task("A")
    # Manually call _task_wrapper directly
    # It should return early because it expects RUNNING
    manager._task_wrapper("A")
    assert task.status == TaskStatus.PENDING


def test_sqlite_operational_error(tmp_path, monkeypatch):
    db_file = str(tmp_path / "test_error.db")
    store = SQLiteStateStore(db_file)

    def mock_connect(*args, **kwargs):
        raise sqlite3.OperationalError("Mocked error")

    with monkeypatch.context() as m:
        m.setattr(sqlite3, "connect", mock_connect)
        assert store.load_tasks() == {}


def test_retry_timer_callback():
    # We want to trigger _mark_ready through the timer in _task_wrapper
    manager = TaskManager(max_workers=1)
    failed_once = False

    def retry_task():
        nonlocal failed_once
        if not failed_once:
            failed_once = True
            raise ValueError("Try again")
        return "OK"

    manager.add_task(
        "T", retry_task, retry_policy=RetryPolicy(max_retries=1, base_delay=0.1)
    )

    task = manager.get_task("T")
    task.status = TaskStatus.RUNNING
    manager._task_wrapper("T")

    # After _task_wrapper, task should be in RETRYING if it failed and has retries left
    assert task.status == TaskStatus.RETRYING

    # Wait for timer to fire and call _mark_ready
    time.sleep(0.3)

    # After timer fires, it should notify.
    ready = manager._get_ready_tasks()
    assert task in ready


def test_shutdown_sequence_complete_log(caplog):
    manager = TaskManager()
    manager._shutdown_requested = True
    with caplog.at_level(logging.INFO):
        manager.execute_all()

    assert any(
        "Shutdown sequence complete" in record.message for record in caplog.records
    )


def test_get_task_thread_safe():
    manager = TaskManager()
    manager.add_task("A", lambda: "done")
    assert manager.get_task("A").task_id == "A"


def test_cancel_task_with_state_store(tmp_path):
    db_file = str(tmp_path / "test_cancel_state.db")
    store = SQLiteStateStore(db_file)
    manager = TaskManager(state_store=store)
    manager.add_task("A", lambda: time.sleep(1))
    manager.cancel_task("A")

    tasks = store.load_tasks()
    assert tasks["A"]["status"] == TaskStatus.CANCELLED


def test_cancel_task_in_futures():
    manager = TaskManager()

    def slow_task():
        time.sleep(2)

    manager.add_task("A", slow_task)
    # Start execution in a separate thread so we can cancel it
    t = threading.Thread(target=manager.execute_all)
    t.start()

    # Wait for it to start
    time.sleep(0.1)
    with manager.lock:
        assert "A" in manager.futures

    manager.cancel_task("A")
    # manager.futures["A"].cancel() should have been called

    manager.shutdown(wait=False)
    t.join()

def test_task_hierarchy_export():
    manager = TaskManager()
    manager.add_task("Root1", lambda: None, priority=2)
    manager.add_task("Child1", lambda: None, priority=1)
    manager.add_task("Child2", lambda: None, priority=2)
    manager.add_task("Root2", lambda: None, priority=1)
    
    manager.add_child("Root1", "Child1")
    manager.add_child("Root1", "Child2")
    
    manager.update_progress("Root1", 50)
    manager.update_progress("Child1", 100)
    
    export = export_task_hierarchy(manager)
    
    assert export["status"] == "success"
    assert export["metadata"]["total_tasks"] == 4
    
    hierarchy = export["data"]["hierarchy"]
    assert len(hierarchy) == 2
    # Roots should be sorted by priority then id: Root2 (1), Root1 (2)
    assert hierarchy[0]["task_id"] == "Root2"
    assert hierarchy[1]["task_id"] == "Root1"
    
    assert hierarchy[1]["progress_pct"] == 50
    assert len(hierarchy[1]["children"]) == 2
    
    children = hierarchy[1]["children"]
    assert children[0]["task_id"] == "Child1"
    assert children[0]["progress_pct"] == 100
    assert children[1]["task_id"] == "Child2"
    
    # Excludes complex objects
    assert "func" not in hierarchy[0]
    assert "result" not in hierarchy[0]
    assert "error" not in hierarchy[0]

def test_add_child_cycle_detection():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    manager.add_task("B", lambda: None)
    manager.add_task("C", lambda: None)
    
    manager.add_child("A", "B")
    manager.add_child("B", "C")
    
    with pytest.raises(TaskCycleError):
        manager.add_child("C", "A")

def test_update_progress_bounds():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    
    manager.update_progress("A", 50)
    assert manager.get_task("A").progress_pct == 50
    
    with pytest.raises(ValueError):
        manager.update_progress("A", 150)
        
    with pytest.raises(ValueError):
        manager.update_progress("A", -10)
        
    with pytest.raises(ValueError, match="Task B not found"):
        manager.update_progress("B", 50)

