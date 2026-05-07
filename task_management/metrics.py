import os
import psutil
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

# Create a custom registry
registry = CollectorRegistry()

# Define metrics
TASK_TOTAL = Counter(
    "task_manager_tasks_total", 
    "Total number of tasks processed", 
    ["status"], 
    registry=registry
)

TASK_LATENCY = Histogram(
    "task_manager_task_latency_seconds", 
    "Latency of task execution in seconds", 
    ["task_id"], 
    registry=registry
)

QUEUE_DEPTH = Gauge(
    "task_manager_queue_depth", 
    "Current number of tasks in the queue", 
    ["state"], 
    registry=registry
)

PROCESS_MEMORY_USAGE = Gauge(
    "task_manager_process_memory_bytes", 
    "Memory usage of the task manager process in bytes", 
    registry=registry
)

PROCESS_CPU_USAGE = Gauge(
    "task_manager_process_cpu_percent", 
    "CPU usage of the task manager process in percent", 
    registry=registry
)

def get_metrics_data():
    """Updates process metrics and returns the latest Prometheus data."""
    process = psutil.Process(os.getpid())
    PROCESS_MEMORY_USAGE.set(process.memory_info().rss)
    PROCESS_CPU_USAGE.set(process.cpu_percent())
    
    return generate_latest(registry), CONTENT_TYPE_LATEST
