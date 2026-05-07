# F-0008: Advanced Scheduling (Cron & Interval)

- **Type:** Feature
- **Priority:** P1
- **Status:** Draft

## Problem
Currently, tasks must be triggered manually or via immediate execution. Users need a way to schedule recurring tasks.

## Requirements
1. Support for Cron-based scheduling strings (e.g., `0 0 * * *`).
2. Support for fixed interval scheduling (e.g., "every 10 minutes").
3. Backend scheduler to monitor and trigger scheduled tasks automatically.
4. UI visibility for scheduled tasks and their next run times.

## Acceptance Criteria
- [ ] Tasks can be configured with a schedule in the creation form.
- [ ] Scheduled tasks are automatically executed by the system at the correct time.
- [ ] Users can view, pause, or delete active schedules from the dashboard.
- [ ] Persistence of schedules across system restarts.

## Out of Scope
- Complex timezone handling (default to UTC).
- Overlap prevention (if a task is still running when the next schedule hits).

## Dependencies
- APScheduler or similar Python scheduling library.
- Persistent state store (SQLite).
