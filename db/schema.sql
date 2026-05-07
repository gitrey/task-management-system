-- Relational database schema for Task Management System

CREATE TABLE IF NOT EXISTS tasks (
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

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    PRIMARY KEY (task_id, depends_on_task_id),
    FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_task_dependencies_task_id ON task_dependencies(task_id);
CREATE INDEX IF NOT EXISTS idx_task_dependencies_depends_on_task_id ON task_dependencies(depends_on_task_id);

CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    level TEXT NOT NULL,
    event TEXT NOT NULL,
    task_id TEXT,
    trace_id TEXT,
    message TEXT,
    details TEXT, -- JSON string for additional metadata
    FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_task_id ON logs(task_id);
CREATE INDEX IF NOT EXISTS idx_logs_trace_id ON logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
