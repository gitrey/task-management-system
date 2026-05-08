variable "project_id" {
  description = "The GCP project ID"
  type        = "STRING"
}

variable "region" {
  description = "The GCP region to deploy to"
  type        = "STRING"
  default     = "us-central1"
}

variable "backend_host" {
  description = "The hostname of the backend service"
  type        = "STRING"
}

variable "container_image" {
  description = "The URI of the container image to deploy"
  type        = "STRING"
}

variable "notification_channel_id" {
  description = "The ID of the notification channel for alerts"
  type        = "STRING"
}
