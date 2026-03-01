import pytest
import time
import threading
from task_management import TaskManager, TaskStatus, TaskCycleError


def test_basic_execution():
    manager = TaskManager(max_workers=2)
    results = []

    def my_task():
        results.append(1)
        return "done"

    manager.add_task("A", my_task)
    manager.execute_all()

    task_a = manager.get_task("A")
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

    manager.add_dependency("A", "C")  # A -> C
    manager.add_dependency("A", "B")  # A -> B
    manager.add_dependency("B", "C")  # B -> C

    # DAG: A -> B -> C
    manager.execute_all()

    assert execution_order == ["A", "B", "C"]
    for task_id in ["A", "B", "C"]:
        assert manager.get_task(task_id).status == TaskStatus.COMPLETED


def test_priority_execution():
    manager = TaskManager(
        max_workers=1
    )  # force sequential execution to guarantee priority test
    execution_order = []

    def make_task(name):
        def _task():
            time.sleep(0.01)  # give a small delay
            execution_order.append(name)

        return _task

    # lower number means higher priority
    manager.add_task("T3", make_task("T3"), priority=3)
    manager.add_task("T1", make_task("T1"), priority=1)
    manager.add_task("T2", make_task("T2"), priority=2)

    # Since all are independent and max_workers=1, they should be picked up in priority order
    manager.execute_all()

    assert execution_order == ["T1", "T2", "T3"]


def test_cycle_detection():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    manager.add_task("B", lambda: None)
    manager.add_task("C", lambda: None)

    manager.add_dependency("A", "B")
    manager.add_dependency("B", "C")

    with pytest.raises(TaskCycleError):
        manager.add_dependency("C", "A")


def test_cascading_failure():
    manager = TaskManager()

    def failing_task():
        raise ValueError("I failed")

    manager.add_task("A", failing_task)
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    manager.execute_all()

    assert manager.get_task("A").status == TaskStatus.FAILED
    assert manager.get_task("B").status == TaskStatus.CANCELLED


def test_manual_cancellation():
    manager = TaskManager()

    def sleep_task():
        time.sleep(0.5)

    manager.add_task("A", sleep_task)
    manager.add_task("B", lambda: None)
    manager.add_task("C", lambda: None)
    manager.add_dependency("A", "B")
    manager.add_dependency("B", "C")

    # Start execution in a separate thread so we can cancel concurrently
    def run_manager():
        manager.execute_all()

    t = threading.Thread(target=run_manager)
    t.start()

    time.sleep(0.1)  # Give A time to start running
    manager.cancel_task("A")
    t.join()

    assert manager.get_task("A").status == TaskStatus.CANCELLED
    assert manager.get_task("B").status == TaskStatus.CANCELLED
    assert manager.get_task("C").status == TaskStatus.CANCELLED


def test_unreachable_tasks():
    manager = TaskManager()
    manager.add_task("A", lambda: None)
    manager.add_task("B", lambda: None)
    manager.add_dependency("A", "B")

    manager.cancel_task("A")
    manager.execute_all()

    assert manager.get_task("A").status == TaskStatus.CANCELLED
    assert manager.get_task("B").status == TaskStatus.CANCELLED
