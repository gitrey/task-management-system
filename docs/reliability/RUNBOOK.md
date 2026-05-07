# Reliability Runbook: Common Operational Procedures

## 1. High Queue Depth Alert
**Symptoms:** `task_manager_queue_depth` is sustained above threshold. Tasks are pending for longer than usual.
**Procedures:**
1. Check process logs for "Executing task" vs "Task completed" events to identify slow tasks.
2. Verify if worker threads are saturated (check `TaskManager` configuration).
3. Inspect `task_manager_process_cpu_percent`. If high, consider vertical scaling.
4. Check if a specific `task_id` is blocking the DAG (e.g., failed and retrying with long delay).

## 2. Backend Health Check Failure (`/healthz` or `/readyz`)
**Symptoms:** Uptime Check alert triggered. Cloud Run instances restarting.
**Procedures:**
1. Check Cloud Run logs for application crashes or unhandled exceptions.
2. Verify Database connectivity:
   - Check if `tasks.db` exists and is writable.
   - Run manual query: `sqlite3 tasks.db "SELECT 1;"`
3. Check for resource exhaustion (Memory/CPU).

## 3. Persistent Task Failures
**Symptoms:** `task_manager_tasks_total{status="failure"}` is increasing.
**Procedures:**
1. Identify the failing `task_id` from the Grafana dashboard or logs.
2. Inspect the `error` field in the `tasks` table for the specific task.
3. Verify if the `RetryPolicy` is correctly configured and if max retries have been reached.
4. If it's a transient infrastructure issue, manual retry may be triggered via `/api/tasks/{task_id}/retry`.

## 4. Database Performance Degraded
**Symptoms:** API latency > 200ms.
**Procedures:**
1. Check SQLite file size and disk IOPS.
2. Ensure `StateStore` operations are indexed (check `task_id` primary keys).
3. If necessary, run `VACUUM;` on the database to reclaim space and defragment.
