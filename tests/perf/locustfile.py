import random
import time
from locust import HttpUser, task, between, events

class TaskManagementAPIUser(HttpUser):
    wait_time = between(1, 2)
    token = None
    username = None

    def on_start(self):
        """Registers a user and logs in to get a token."""
        self.username = f"user_{int(time.time())}_{random.randint(0, 1000)}"
        password = "password123"
        
        # Register
        self.client.post("/register", json={
            "username": self.username,
            "password": password,
            "email": f"{self.username}@example.com"
        })
        
        # Login
        response = self.client.post("/token", data={
            "username": self.username,
            "password": password
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Failed to login: {response.text}")

    @task(3)
    def create_and_execute_dag(self):
        """Simulates creating a 5-node DAG and executing it."""
        if not self.token: return

        # 1. Create 5 tasks
        task_ids = []
        for i in range(5):
            name = f"LoadTest_Task_{int(time.time())}_{i}_{random.randint(0, 1000)}"
            response = self.client.post("/api/tasks", headers=self.headers, json={
                "name": name,
                "priority": random.randint(1, 10),
                "max_retries": 3,
                "base_delay": 1.0,
                "dependencies": []
            })
            if response.status_code == 200:
                task_ids.append(response.json()["id"])
        
        # 2. Execute all
        self.client.post("/api/execute", headers=self.headers)
        
        # 3. Wait and check status
        for _ in range(3):
            time.sleep(1)
            response = self.client.get("/api/tasks", headers=self.headers)
            if response.status_code == 200:
                tasks = response.json()
                our_tasks = [t for t in tasks if t["id"] in task_ids]
                if all(t["status"] == "COMPLETED" for t in our_tasks):
                    break

    @task(1)
    def check_metrics(self):
        """Probes the /metrics endpoint (F-0010 verification)."""
        # Metrics endpoint is public based on main.py
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                content = response.text
                expected_metrics = [
                    "task_manager_tasks_total",
                    "task_manager_task_latency_seconds",
                    "task_manager_queue_depth",
                    "task_manager_process_cpu_percent",
                    "task_manager_process_memory_bytes"
                ]
                missing = [m for m in expected_metrics if m not in content]
                if not missing:
                    response.success()
                else:
                    response.failure(f"Prometheus metrics missing: {', '.join(missing)}")
            else:
                response.failure(f"Metrics endpoint returned {response.status_code}")

    @task(5)
    def get_tasks_list(self):
        """High frequency task to simulate dashboard polling."""
        if not self.token: return
        self.client.get("/api/tasks", headers=self.headers)

    @task(2)
    def check_logs(self):
        """Simulates log viewer polling."""
        if not self.token: return
        self.client.get("/api/logs?limit=50", headers=self.headers)
