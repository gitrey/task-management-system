import time
import logging
from locust import User, task, between, events
from task_management import TaskManager

# Disable TaskManager's internal structured logging to keep Locust output clean
logging.getLogger("task_management").setLevel(logging.ERROR)

def heavy_task():
    """Simulates a task that takes some time and resources."""
    # Fibonacci calculation to consume some CPU
    def fib(n):
        if n <= 1: return n
        return fib(n-1) + fib(n-2)
    fib(20) 
    return "completed"

class TaskManagerLoadTest(User):
    """Simulates users interacting with the TaskManager library."""
    wait_time = between(0.1, 0.5)

    @task
    def execute_dag_scenario(self):
        """Creates a DAG with 5 tasks and multiple dependencies, then executes it."""
        start_time = time.perf_counter()
        name = "execute_dag_5_tasks"
        
        try:
            manager = TaskManager(max_workers=4)
            
            # Define tasks
            manager.add_task("T1", heavy_task, priority=1)
            manager.add_task("T2", heavy_task, priority=2)
            manager.add_task("T3", heavy_task, priority=1)
            manager.add_task("T4", heavy_task, priority=3)
            manager.add_task("T5", heavy_task, priority=0)
            
            # Define complex dependencies
            # T1 -> T2
            # T1 -> T3
            # T2 -> T4
            # T3 -> T4
            # T4 -> T5
            manager.add_dependency("T1", "T2")
            manager.add_dependency("T1", "T3")
            manager.add_dependency("T2", "T4")
            manager.add_dependency("T3", "T4")
            manager.add_dependency("T4", "T5")
            
            manager.execute_all(timeout=10.0)
            
            total_time = (time.perf_counter() - start_time) * 1000
            events.request.fire(
                request_type="LibraryCall",
                name=name,
                response_time=total_time,
                response_length=0,
                exception=None,
            )
        except Exception as e:
            total_time = (time.perf_counter() - start_time) * 1000
            events.request.fire(
                request_type="LibraryCall",
                name=name,
                response_time=total_time,
                response_length=0,
                exception=e,
            )

    @task(3)
    def simple_task_scenario(self):
        """Simulates a single high-priority task execution."""
        start_time = time.perf_counter()
        name = "execute_single_task"
        
        try:
            manager = TaskManager(max_workers=1)
            manager.add_task("S1", heavy_task, priority=0)
            manager.execute_all(timeout=5.0)
            
            total_time = (time.perf_counter() - start_time) * 1000
            events.request.fire(
                request_type="LibraryCall",
                name=name,
                response_time=total_time,
                response_length=0,
                exception=None,
            )
        except Exception as e:
            total_time = (time.perf_counter() - start_time) * 1000
            events.request.fire(
                request_type="LibraryCall",
                name=name,
                response_time=total_time,
                response_length=0,
                exception=e,
            )
