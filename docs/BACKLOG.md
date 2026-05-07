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
- [x] **F-0007: AI-Assisted DAG Generation (GENDEV-97)**
  - **Priority:** P2
  - **Scope:** LLM integration for natural language workflow generation.
  - **Dependencies:** F-0004
  - **Spec:** [spec](docs/specs/F-0007-ai-dag-generation.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Create LLM integration service using Google Vertex AI/Gemini (SWE-1)
    - [x] Implement backend endpoint for natural language workflow parsing (SWE-1)
    - [x] Add "Generate Workflow" UI component to the dashboard (SWE-2)
    - [x] Integrate visual preview logic using existing DAG visualizer (SWE-2)
    - [x] Verify AI-generated DAG correctness with edge-case descriptions (SWE-Test)
- [x] **F-0008: Advanced Scheduling (GENDEV-98)**
  - **Priority:** P1
  - **Scope:** Cron and interval-based recurring task execution.
  - **Dependencies:** SQLite
  - **Spec:** [spec](docs/specs/F-0008-advanced-scheduling.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Add `schedule` column to database tasks table (DB-1)
    - [x] Integrate APScheduler into the backend TaskManager (SWE-1)
    - [x] Implement recurring task trigger and persistence logic (SWE-1)
    - [x] Update task creation form to support Cron/Interval inputs (SWE-2)
    - [x] Add "Upcoming Runs" view to the dashboard (SWE-2)
- [x] **F-0009: Security & Multi-tenancy (GENDEV-99)**
  - **Priority:** P1
  - **Scope:** OAuth2/JWT authentication and project isolation.
  - **Dependencies:** FastAPI
  - **Spec:** [spec](docs/specs/F-0009-security-multi-tenancy.md)
  - **Status:** COMPLETED
  - **Tasks:**
    - [x] Design and implement Users and Projects database schema (DB-1)
    - [x] Implement JWT-based authentication in FastAPI (SWE-1)
    - [x] Add multi-tenancy filters to all task management queries (SWE-1)
    - [x] Create Login page and session management in the frontend (SWE-2)
    - [x] Add project selection and management UI (SWE-2)
    - [x] Run security scan for authentication bypass vulnerabilities (Secops-1)
- [ ] **F-0010: Observability (GENDEV-100)**
  - **Priority:** P2
  - **Scope:** Prometheus metrics and Grafana dashboard.
  - **Dependencies:** Infrastructure support
  - **Spec:** [spec](docs/specs/F-0010-observability.md)
  - **Status:** IN PROGRESS
  - **Tasks:**
    - [x] Integrate `prometheus_client` and define core system metrics (SWE-1)
    - [x] Implement `/metrics` endpoint in FastAPI (SWE-1)
    - [x] Add resource monitoring (CPU/RAM) to TaskManager (SWE-1)
    - [x] Create Prometheus configuration and Grafana dashboard JSON (SRE-1)
    - [ ] Finalize backend metrics alignment with SLO specs (SWE-1)
    - [x] Verify metrics accuracy during high-concurrency load (Perf-Test)
