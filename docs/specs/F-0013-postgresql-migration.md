# F-0013: Database Migration to PostgreSQL (GENDEV-104)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
The current application uses SQLite for local state management. For a scalable cloud deployment, we need to transition to a more robust RDBMS like PostgreSQL and ensure the application can connect to it dynamically.

## Requirements
1. Design the logical PostgreSQL schema mirroring the existing SQLite structure (Tasks, Dependencies, Projects, Users, Logs).
2. Create database migrations for PostgreSQL (e.g., using a tool like Alembic or simple SQL scripts).
3. Generate robust test seed data for PostgreSQL (e.g., 10-node DAG).
4. Update the application backend (`persistence.py`, `manager.py`, etc.) to support PostgreSQL connection strings via environment variables.

## Acceptance Criteria
- [ ] PostgreSQL schema is successfully applied to the Cloud SQL instance.
- [ ] The application backend can perform CRUD operations on the PostgreSQL database.
- [ ] Seed data is correctly loaded and visible in the dashboard.
- [ ] The application maintains high test coverage (>= 90%) after the persistence layer refactor.

## Out of Scope
- Automated data migration from SQLite to PostgreSQL (fresh start in Cloud SQL).
- Performance tuning of PostgreSQL indices (standard indices only).

## Dependencies
- F-0011 (Cloud SQL availability).
- Python PostgreSQL drivers (e.g., `psycopg2-binary` or `asyncpg`).
