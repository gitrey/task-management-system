# F-0005: Task Management Controls & API (GENDEV-95)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
Users need to manually intervene in task execution (cancel, retry) and trigger the execution process from the dashboard.

## Requirements
1. Add clickable controls on each task node in the graph to:
    - Cancel a task.
    - Manually retry a failed task.
    - Inspect execution outcomes (`task.result`).
2. Expose REST or JSON-RPC backend endpoints to:
    - Execute `execute_all()`.
    - Manage individual tasks (cancel/retry).
3. Ensure these operations are safe and non-interactive.

## Acceptance Criteria
- [ ] Clicking "Cancel" on a node successfully cancels the task in the backend.
- [ ] A "Run All" button on the dashboard triggers the `execute_all()` process.
- [ ] Task result/error details are visible upon clicking a node.

## Out of Scope
- Scheduling tasks for future execution times.
- Bulk actions (e.g., "Cancel All").

## Dependencies
- Backend API endpoints.
- F-0004 (DAG Graph Visualizer) for UI integration.
