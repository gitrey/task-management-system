# F-0003: Dynamic Task Scheduling Form (GENDEV-93)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
Users currently manage tasks via Python scripts. We need a web UI to schedule tasks to make the system accessible to non-developers.

## Requirements
1. Create an intuitive, responsive web form to schedule new tasks.
2. Form inputs must include:
    - Task Name
    - Priority Level (1-10)
    - Retry Policy (Max Retries, Base Delay)
    - Dependency selection (select existing tasks to establish DAG parent-child relations).
3. Backend must leverage Pydantic model validation to validate configurations before adding them to the `TaskManager`.

## Acceptance Criteria
- [ ] Task Scheduling Form is visible and responsive on the dashboard.
- [ ] Valid task data submitted via the form is correctly stored in the `TaskManager`.
- [ ] Pydantic validation errors are returned to the frontend and displayed to the user.
- [ ] Dependency dropdown correctly lists existing tasks.

## Out of Scope
- Advanced cron-like scheduling (e.g., "every Monday").
- User authentication/authorization.

## Dependencies
- Pydantic
- Backend API (FastAPI or Flask)
