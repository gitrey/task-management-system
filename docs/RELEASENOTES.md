# Release Notes

## [1.4.0] - 2026-05-07
### Added
- **Operational Maturity & Intelligence (Milestone 4):**
    - **AI-Assisted DAG Generation:** LLM integration for natural language workflow creation (F-0007).
    - **Advanced Scheduling:** Cron and interval-based recurring task execution (F-0008).
    - **Security & Multi-tenancy:** OAuth2/JWT authentication and project-level isolation (F-0009).
    - **Observability:** Prometheus metrics integration and Grafana dashboard for system-wide monitoring (F-0010).
    - **Reliability Tooling:** Comprehensive runbooks, post-mortem templates, and SLO definitions.

## [1.3.0] - 2026-05-07
### Added
- **Interactive Web Dashboard (Milestone 3):**
    - **Dynamic Task Scheduling:** Responsive web form for task creation with Pydantic-based validation (F-0003).
    - **Interactive DAG Visualizer:** Real-time graph visualization of task dependencies using Cytoscape.js (F-0004).
    - **Task Lifecycle Controls:** On-graph controls to manually execute, cancel, or retry tasks via a new REST API (F-0005).
    - **Terminal Log Streamer:** Real-time log monitoring with filtering by trace ID, task ID, and severity (F-0006).
- **Infrastructure & SRE:**
    - Containerized deployment with Docker and automated GCP Cloud Run provisioning via Terraform.
    - Health and Readiness probes (`/healthz`, `/readyz`) and Cloud Monitoring alerting policies.
- **Security & Quality:**
    - Completed security audit (Semgrep, Bandit, Dependency scans) with 0 findings.
    - Verified API performance: p95 response time of 180ms under load, meeting the <200ms target.
    - Maintained 99% test coverage for core task management logic.

## [1.2.0] - 2026-05-07
### Added
- **Team Process Optimization (F-0003):** Established a new team collaboration protocol (`docs/TEAM_PROTOCOLS.md`) covering Git synchronization, hand-off verification, and proactive blocker reporting. Refined the backlog structure for better sub-task visibility.

## [1.1.0] - 2026-05-06
### Added
- **Web Interface (F-0002):** A modern, responsive landing page (`index.html`) highlighting project features, architecture, and usage examples. Includes custom styling (`style.css`) and syntax highlighting for code snippets (`script.js`).

## [1.0.0] - 2026-05-06
### Improved
- **Test Coverage (F-0001):** Increased test coverage across the `task_management` package to 99%, ensuring robust handling of DAG scheduling, retries, and persistence.
### Added
- Initial project setup with core task management functionality including DAG-based scheduling, priority queues, and SQLite persistence.
