# Reliability & Observability Documentation

This directory contains the core documentation for maintaining the stability, availability, and observability of the Task Management System.

## Contents

1.  **[Service Level Objectives (SLOs)](SLO.md)**
    *   Defines our SLIs (Availability, Latency, Error Rate) and our target objectives.
    *   Includes technical specifications for `/healthz` and `/readyz` probes.

2.  **[Operational Runbook](RUNBOOK.md)**
    *   Standard operating procedures for responding to common alerts (High Queue Depth, Health Check failures, etc.).
    *   Basic troubleshooting steps for the persistence layer and task execution engine.

3.  **[Incident Post-Mortem Template](POST_MORTEM_TEMPLATE.md)**
    *   Standardized format for documenting incidents, root cause analysis (RCA), and tracking corrective actions.

## Monitoring Infrastructure

The monitoring stack is provisioned via Terraform in `terraform/monitoring/` and includes:
*   **GCP Uptime Checks**: Probing the service every 60 seconds.
*   **Alerting Policies**: High CPU, High Memory, High Error Rate, and Availability alerts.
*   **Prometheus**: Scraping internal metrics from `/metrics`.
*   **Grafana Dashboard**: Visualizing task lifecycle and system performance (see `monitoring/grafana/dashboards/task_manager.json`).
