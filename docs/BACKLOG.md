# Backlog

## Milestone 1: Initial Release
- [x] **F-0001: Increase test coverage to 90% (GENDEV-90)**
  - **Priority:** P1
  - **Scope:** Complete coverage of `task_management/` package.
  - **Dependencies:** `pytest`, `pytest-cov`
  - **Spec:** [spec](docs/specs/F-0001-increase-test-coverage.md)
  - **Status:** COMPLETED
  - **Assigned:** SWE-1

## Milestone 2: Web Presence
- [x] **F-0002: Web Interface (GENDEV-91)**
  - **Priority:** P1
  - **Scope:** Responsive landing page `index.html` with project details, features, structure, and sample usage.
  - **Dependencies:** None
  - **Spec:** [spec](docs/specs/F-0002-web-interface.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Create `index.html` with full content and SEO metadata (SWE-1)
    - [x] Create `style.css` for modern, responsive styling and typography (SWE-2)
    - [x] Add `script.js` for code syntax highlighting and UI interactions (SWE-2)
    - [x] Final verification of design and responsiveness (SWE-Test)

## Milestone 2.5: Process Optimization
- [x] **F-0002.5: Team Process Retrospective & Agent Protocol Improvements (GENDEV-92)**
  - **Priority:** P2
  - **Spec:** [spec](docs/specs/F-0002-process-improvements.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Create `docs/TEAM_PROTOCOLS.md` with standardized git and communication rules (Assigned: SWE-1)
    - [x] Refine `docs/BACKLOG.md` structure to support granular sub-task tracking (Assigned: TPM)
    - [x] Brief all agents on new role refinements and sync protocols (Assigned: TPM)

## Milestone 3: Interactive Dashboard

- [x] **F-0003: Dynamic Task Scheduling Form (GENDEV-93)**
  - **Priority:** P1
  - **Scope:** Web form for task creation with Pydantic validation.
  - **Dependencies:** Backend API
  - **Spec:** [spec](docs/specs/F-0003-dynamic-task-scheduling-form.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Create SQLite migrations for task and dependency tables (DB-1)
    - [x] Implement Pydantic models for task validation (SWE-1)
    - [x] Develop dynamic HTML form with interactive field validation (SWE-2)
    - [x] Add unit tests for form validation logic (SWE-Test)

- [x] **F-0004: Interactive DAG Graph Visualizer (GENDEV-94)**
  - **Priority:** P1
  - **Scope:** Real-time DAG visualization using Cytoscape.js.
  - **Dependencies:** F-0003
  - **Spec:** [spec](docs/specs/F-0004-dag-graph-visualizer.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Seed 10-node DAG dataset for visualization testing (DB-1)
    - [x] Integrate Cytoscape.js and implement basic graph layout (SWE-2)
    - [x] Add interactive nodes with state-based color coding (SWE-2)
    - [x] Capture baseline and interaction-state screenshots (UI-Test)

- [x] **F-0005: Task Management Controls & API (GENDEV-95)**
  - **Priority:** P1
  - **Scope:** Controls for cancel/retry and execution API.
  - **Dependencies:** F-0004
  - **Spec:** [spec](docs/specs/F-0005-task-management-controls.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Implement REST API endpoints for task lifecycle (cancel, retry) (SWE-1)
    - [x] Add UI control panel with interactive buttons (SWE-2)
    - [x] Verify API coverage >= 90% (SWE-Test)
    - [x] Run Locust load test (p95 < 200ms) (Perf-Test)

- [x] **F-0006: Terminal Log Stream Viewer (GENDEV-96)**
  - **Priority:** P1
  - **Scope:** Dark-mode terminal log viewer with filtering.
  - **Dependencies:** JSON logging
  - **Spec:** [spec](docs/specs/F-0006-terminal-log-viewer.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Create logs table migration and seed sample logs (DB-1)
    - [x] Update logging module to support JSON streaming (SWE-1)
    - [x] Implement frontend log viewer component with filtering (SWE-2)
    - [x] Add health/ready checks for deployment (SRE-1)
    - [x] Final security scan and OpenAPI spec generation (Secops-1)

## Milestone 4: Operational Maturity & Intelligence
- [ ] **F-0007: AI-Assisted DAG Generation (GENDEV-97)**
  - **Priority:** P2
  - **Scope:** LLM integration for natural language workflow generation.
  - **Dependencies:** F-0004
  - **Spec:** [spec](docs/specs/F-0007-ai-dag-generation.md)
  - **Status:** TO DO
- [ ] **F-0008: Advanced Scheduling (GENDEV-98)**
  - **Priority:** P1
  - **Scope:** Cron and interval-based recurring task execution.
  - **Dependencies:** SQLite
  - **Spec:** [spec](docs/specs/F-0008-advanced-scheduling.md)
  - **Status:** IN PROGRESS
  - **Tasks:**
    - [x] Design scheduling schema and migration (DB-1)
    - [ ] Implement APScheduler integration (SWE-1)
    - [ ] Add scheduling fields to task creation form (SWE-2)
- [ ] **F-0009: Security & Multi-tenancy (GENDEV-99)**
  - **Priority:** P1
  - **Scope:** OAuth2/JWT authentication and project isolation.
  - **Dependencies:** FastAPI
  - **Spec:** [spec](docs/specs/F-0009-security-multi-tenancy.md)
  - **Status:** IN PROGRESS
  - **Tasks:**
    - [x] Design multi-tenancy schema (Users, Projects) and migration (DB-1)
    - [ ] Implement JWT authentication and login API (SWE-1)
    - [ ] Add project selection and user management to UI (SWE-2)
- [ ] **F-0010: Observability (GENDEV-100)**
  - **Priority:** P2
  - **Scope:** Prometheus metrics and Grafana dashboard.
  - **Dependencies:** Infrastructure support
  - **Spec:** [spec](docs/specs/F-0010-observability.md)
  - **Status:** TO DO
