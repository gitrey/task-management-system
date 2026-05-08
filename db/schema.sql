-- Relational database schema for Task Management System

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at REAL DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at REAL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (owner_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS project_members (
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schedules (
    schedule_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    cron_expression TEXT, -- e.g., "0 0 * * *"
    interval_seconds INTEGER, -- e.g., 600 for 10 minutes
    next_run_at REAL,
    is_active INTEGER DEFAULT 1, -- 0 for paused, 1 for active
    created_at REAL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    schedule_id TEXT,
    name TEXT,
    priority INTEGER DEFAULT 0,
    status TEXT DEFAULT 'PENDING',
    retries INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    base_delay REAL DEFAULT 1.0,
    max_delay REAL DEFAULT 60.0,
    result TEXT,
    error TEXT,
    trace_id TEXT NOT NULL,
    created_at REAL DEFAULT (strftime('%s', 'now')),
    updated_at REAL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedules (schedule_id) ON DELETE SET NULL
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
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_schedule_id ON tasks(schedule_id);
CREATE INDEX IF NOT EXISTS idx_schedules_project_id ON schedules(project_id);

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
