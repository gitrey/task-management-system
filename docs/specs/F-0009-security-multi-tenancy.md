# F-0009: Security & Multi-tenancy (GENDEV-99)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
The dashboard is currently open to anyone with the URL, and there is no isolation between different users' tasks.

## Requirements
1. Implement user authentication using OAuth2 or JWT.
2. Provide a login interface on the web dashboard.
3. Support for project-level isolation (tasks belong to a project, users are members of projects).
4. Secure API endpoints requiring valid authentication tokens.

## Acceptance Criteria
- [ ] Users must log in to access the dashboard.
- [ ] Users can only see and manage tasks within projects they have access to.
- [ ] API calls return 401 Unauthorized without a valid token.
- [ ] Basic project management UI (create project, add user).

## Out of Scope
- Granular RBAC (Role-Based Access Control) within projects (all members are admins).
- Self-service password reset.

## Dependencies
- FastAPI Security / PyJWT.
- Database schema updates for Users and Projects.
