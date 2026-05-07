-- V2: Add logs table for F-0006 Terminal Log Viewer

CREATE TABLE logs (
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

CREATE INDEX idx_logs_task_id ON logs(task_id);
CREATE INDEX idx_logs_trace_id ON logs(trace_id);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
