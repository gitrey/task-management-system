-- Seed data for Task Management System

-- 1. Insert Users
INSERT INTO users (user_id, username, email, password_hash) VALUES ('user-1', 'admin', 'admin@example.com', 'pbkdf2:sha256:600000$hashedpassword');
INSERT INTO users (user_id, username, email, password_hash) VALUES ('user-2', 'developer', 'dev@example.com', 'pbkdf2:sha256:600000$hashedpassword');

-- 2. Insert Projects
INSERT INTO projects (project_id, name, owner_id) VALUES ('project-1', 'Main Infrastructure', 'user-1');
INSERT INTO projects (project_id, name, owner_id) VALUES ('project-2', 'Data Pipeline', 'user-2');

-- 3. Insert Project Members
INSERT INTO project_members (project_id, user_id) VALUES ('project-1', 'user-1');
INSERT INTO project_members (project_id, user_id) VALUES ('project-1', 'user-2');
INSERT INTO project_members (project_id, user_id) VALUES ('project-2', 'user-2');

-- 4. Insert Schedules
INSERT INTO schedules (schedule_id, project_id, name, cron_expression, next_run_at) VALUES ('sched-1', 'project-1', 'Daily Cleanup', '0 0 * * *', 1715126400.0);
INSERT INTO schedules (schedule_id, project_id, name, interval_seconds, next_run_at) VALUES ('sched-2', 'project-2', 'Metric Aggregator', 600, 1715070600.0);

-- 5. Insert Tasks
-- Project 1 Tasks
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('task-1', 'project-1', 1, 'COMPLETED', 'trace-1', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('task-2', 'project-1', 2, 'COMPLETED', 'trace-2', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('task-3', 'project-1', 2, 'COMPLETED', 'trace-3', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('task-4', 'project-1', 3, 'RUNNING', 'trace-4', 0);

-- Project 2 Tasks (The 10-node DAG from previous seed)
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-1', 'project-2', 1, 'COMPLETED', 'trace-p2-1', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-2', 'project-2', 2, 'COMPLETED', 'trace-p2-2', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-3', 'project-2', 2, 'COMPLETED', 'trace-p2-3', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-4', 'project-2', 3, 'RUNNING', 'trace-p2-4', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-5', 'project-2', 4, 'RETRYING', 'trace-p2-5', 1);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries, error) VALUES ('p2-task-6', 'project-2', 4, 'FAILED', 'trace-p2-6', 3, 'Simulated failure for testing');
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-7', 'project-2', 5, 'PENDING', 'trace-p2-7', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-8', 'project-2', 6, 'PENDING', 'trace-p2-8', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-9', 'project-2', 7, 'PENDING', 'trace-p2-9', 0);
INSERT INTO tasks (task_id, project_id, priority, status, trace_id, retries) VALUES ('p2-task-10', 'project-2', 7, 'PENDING', 'trace-p2-10', 0);

-- 6. Insert Dependencies
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-2', 'task-1');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-3', 'task-1');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-4', 'task-2');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-4', 'task-3');

INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-2', 'p2-task-1');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-3', 'p2-task-1');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-4', 'p2-task-2');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-4', 'p2-task-3');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-5', 'p2-task-4');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-6', 'p2-task-4');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-7', 'p2-task-5');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-7', 'p2-task-6');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-8', 'p2-task-7');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-9', 'p2-task-8');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('p2-task-10', 'p2-task-8');

-- 7. Seed logs
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070000.0, 'INFO', 'TASK_CREATED', 'task-1', 'trace-1', 'Task 1 created');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070005.0, 'INFO', 'TASK_STARTED', 'task-1', 'trace-1', 'Task 1 started execution');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070010.0, 'INFO', 'TASK_COMPLETED', 'task-1', 'trace-1', 'Task 1 completed successfully');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070015.0, 'INFO', 'TASK_STARTED', 'task-2', 'trace-2', 'Task 2 started execution');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070020.0, 'INFO', 'TASK_COMPLETED', 'task-2', 'trace-2', 'Task 2 completed successfully');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070025.0, 'INFO', 'TASK_STARTED', 'p2-task-4', 'trace-p2-4', 'Task 4 started execution');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070030.0, 'WARNING', 'TASK_RETRYING', 'p2-task-5', 'trace-p2-5', 'Task 5 failed, retrying (1/3)');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message, details) VALUES (1715070035.0, 'ERROR', 'TASK_FAILED', 'p2-task-6', 'trace-p2-6', 'Task 6 failed permanently', '{"error": "Simulated failure for testing"}');
