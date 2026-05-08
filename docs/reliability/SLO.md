# Service Level Objectives (SLOs) - Task Management System

## Service Level Indicators (SLIs)

1. **Availability**: The percentage of successful requests to the `/healthz` and `/readyz` endpoints over a 30-day window.
2. **Latency**: The time it takes for the backend to respond to a task execution request (p95).
3. **Error Rate**: The percentage of failed task executions due to system errors (excluding user-defined task failures).

## Objectives

| SLI | Target | Window |
| :--- | :--- | :--- |
| **Availability** | 99.9% | 30 days |
| **Latency (Execution API)** | < 200ms (p95) | 30 days |
| **Success Rate (Internal)** | 99.5% | 30 days |

## Health Check Specifications

### 1. Liveness Probe (`/healthz`)
- **Purpose**: Indicates if the service is running.
- **Path**: `/healthz`
- **Method**: `GET`
- **Expected Status Code**: `200 OK`
- **Expected JSON Body**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-05-07T13:00:00Z"
  }
  ```
- **Check logic**: Basic process sanity.

### 2. Readiness Probe (`/readyz`)
- **Purpose**: Indicates if the service is ready to accept traffic.
- **Path**: `/readyz`
- **Method**: `GET`
- **Expected Status Code**: `200 OK` (if ready), `503 Service Unavailable` (if not ready)
- **Expected JSON Body**:
  ```json
  {
    "status": "ready",
    "components": {
      "database": "connected",
      "storage": "writable"
    }
  }
  ```
- **Check logic**:
    - Database connection is active.
    - Persistence layer is writable.
    - Logging system is initialized.
