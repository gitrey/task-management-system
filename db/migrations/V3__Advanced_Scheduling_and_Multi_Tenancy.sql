-- V3: Advanced Scheduling and Multi-Tenancy

-- 1. Create Users Table for F-0009
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at REAL DEFAULT (strftime('%s', 'now'))
);

-- 2. Create Projects Table for F-0009
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at REAL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (owner_id) REFERENCES users (user_id)
);

-- 3. Create Project Members Table for F-0009
CREATE TABLE project_members (
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- 4. Create Schedules Table for F-0008
CREATE TABLE schedules (
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

-- 5. Update tasks table for Multi-tenancy and Scheduling
-- Since SQLite doesn't support adding FKs to existing tables, we recreate it.

PRAGMA foreign_keys=OFF;

CREATE TABLE tasks_new (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL, -- All tasks must belong to a project now
    schedule_id TEXT,
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

-- Note: We need a default project for existing tasks to migrate safely
-- We'll insert a placeholder user and project in the same transaction.
INSERT INTO users (user_id, username, email, password_hash) 
VALUES ('system-user', 'system', 'system@example.com', 'N/A');

INSERT INTO projects (project_id, name, owner_id) 
VALUES ('default-project', 'Default Project', 'system-user');

-- Copy existing tasks to new table
INSERT INTO tasks_new (
    task_id, project_id, priority, status, retries, max_retries, 
    base_delay, max_delay, result, error, trace_id
)
SELECT 
    task_id, 'default-project', priority, status, retries, max_retries, 
    base_delay, max_delay, result, error, trace_id
FROM tasks;

DROP TABLE tasks;
ALTER TABLE tasks_new RENAME TO tasks;

PRAGMA foreign_keys=ON;

-- 6. Add indexes
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_schedules_project_id ON schedules(project_id);
CREATE INDEX idx_tasks_schedule_id ON tasks(schedule_id);
