-- V1: Initial Schema for tasks and dependencies

CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    priority INTEGER DEFAULT 0,
    status TEXT DEFAULT 'PENDING',
    retries INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    base_delay REAL DEFAULT 1.0,
    max_delay REAL DEFAULT 60.0,
    result TEXT,
    error TEXT,
    trace_id TEXT NOT NULL
);

CREATE TABLE task_dependencies (
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    PRIMARY KEY (task_id, depends_on_task_id),
    FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE
);

CREATE INDEX idx_task_dependencies_task_id ON task_dependencies(task_id);
CREATE INDEX idx_task_dependencies_depends_on_task_id ON task_dependencies(depends_on_task_id);
