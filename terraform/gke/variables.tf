variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "network_name" {
  description = "The name of the VPC network"
  type        = string
  default     = "task-mgmt-vpc"
}

variable "subnet_name" {
  description = "The name of the GKE subnet"
  type        = string
  default     = "gke-subnet"
}

variable "cluster_name" {
  description = "The name of the GKE cluster"
  type        = string
  default     = "task-mgmt-cluster"
}
