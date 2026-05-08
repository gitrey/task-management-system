# F-0006: Terminal Log Stream Viewer (GENDEV-96)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
Auditing task execution logs currently requires checking files or console output. A dashboard-integrated log viewer is needed for real-time monitoring.

## Requirements
1. Build a sleek, dark-mode terminal log component on the dashboard.
2. Parse and stream JSON structured logs from the backend.
3. Allow users to filter logs by:
    - `trace_id`
    - `task_id`
    - Severity (INFO, WARNING, ERROR)

## Acceptance Criteria
- [ ] Log viewer displays logs in real-time as tasks are executed.
- [ ] Logs are formatted for readability (not just raw JSON).
- [ ] Filters correctly limit the displayed logs.
- [ ] Dark-mode styling is consistent with the rest of the dashboard.

## Out of Scope
- Exporting logs to CSV/JSON.
- Infinite scroll for historical logs (limit to last 100-500 entries).

## Dependencies
- Logging backend (JSON structured logs).
- WebSocket or similar for streaming.
