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
