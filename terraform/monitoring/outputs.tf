output "service_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "The URL of the deployed Cloud Run service"
}

output "uptime_check_id" {
  value       = google_monitoring_uptime_check_config.http_check.uptime_check_id
  description = "The ID of the created uptime check"
}
