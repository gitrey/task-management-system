# F-0011: GCP Infrastructure Provisioning (Terraform) (GENDEV-102)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
The application currently runs in local containers or Cloud Run. We need a more robust, private, and scalable infrastructure on GCP using GKE and Cloud SQL, managed via declarative Infrastructure as Code (IaC).

## Requirements
1. Design Terraform configurations to provision a private VPC Network with a NAT Gateway.
2. Provision a private GKE (Autopilot) cluster for application hosting.
3. Provision a private Cloud SQL (PostgreSQL) instance with automatic backups.
4. Set up Google Secret Manager to dynamically store and manage database connection strings and other secrets.
5. Implement Least-Privilege IAM Service Accounts and Workload Identity bindings for GKE-to-GCP resource access.

## Acceptance Criteria
- [ ] Terraform plan executes successfully without errors.
- [ ] VPC, GKE Autopilot, and Cloud SQL instance are visible in the GCP console and correctly configured as private.
- [ ] Secret Manager contains the required database secrets.
- [ ] IAM roles are correctly assigned to the application's Service Account.

## Out of Scope
- Multi-region redundancy (single region deployment only).
- Advanced Cloud Armor WAF configurations.

## Dependencies
- GCP Project with billing enabled.
- Terraform CLI.
