# Release Notes

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
    - Verified API performance (p95 < 200ms) and maintained high test coverage.

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
