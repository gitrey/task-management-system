-- Seed data for 10-node DAG visualization testing

-- Insert tasks
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-1', 1, 'COMPLETED', 'trace-1', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-2', 2, 'COMPLETED', 'trace-2', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-3', 2, 'COMPLETED', 'trace-3', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-4', 3, 'RUNNING', 'trace-4', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-5', 4, 'RETRYING', 'trace-5', 1);
INSERT INTO tasks (task_id, priority, status, trace_id, retries, error) VALUES ('task-6', 4, 'FAILED', 'trace-6', 3, 'Simulated failure for testing');
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-7', 5, 'PENDING', 'trace-7', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-8', 6, 'PENDING', 'trace-8', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-9', 7, 'PENDING', 'trace-9', 0);
INSERT INTO tasks (task_id, priority, status, trace_id, retries) VALUES ('task-10', 7, 'PENDING', 'trace-10', 0);

-- Insert dependencies
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-2', 'task-1');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-3', 'task-1');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-4', 'task-2');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-4', 'task-3');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-5', 'task-4');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-6', 'task-4');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-7', 'task-5');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-7', 'task-6');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-8', 'task-7');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-9', 'task-8');
INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES ('task-10', 'task-8');

-- Seed logs for F-0006 visualization
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070000.0, 'INFO', 'TASK_CREATED', 'task-1', 'trace-1', 'Task 1 created');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070005.0, 'INFO', 'TASK_STARTED', 'task-1', 'trace-1', 'Task 1 started execution');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070010.0, 'INFO', 'TASK_COMPLETED', 'task-1', 'trace-1', 'Task 1 completed successfully');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070015.0, 'INFO', 'TASK_STARTED', 'task-2', 'trace-2', 'Task 2 started execution');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070020.0, 'INFO', 'TASK_COMPLETED', 'task-2', 'trace-2', 'Task 2 completed successfully');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070025.0, 'INFO', 'TASK_STARTED', 'task-4', 'trace-4', 'Task 4 started execution');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message) VALUES (1715070030.0, 'WARNING', 'TASK_RETRYING', 'task-5', 'trace-5', 'Task 5 failed, retrying (1/3)');
INSERT INTO logs (timestamp, level, event, task_id, trace_id, message, details) VALUES (1715070035.0, 'ERROR', 'TASK_FAILED', 'task-6', 'trace-6', 'Task 6 failed permanently', '{"error": "Simulated failure for testing"}');
