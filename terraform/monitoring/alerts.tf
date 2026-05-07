resource "google_monitoring_uptime_check_config" "http_check" {
  display_name = "Task Management Backend Uptime Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/healthz"
    port         = "8080"
    use_ssl      = false
    validate_ssl = false
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.backend_host
    }
  }
}

resource "google_monitoring_alert_policy" "uptime_alert" {
  display_name = "Backend Down Alert"
  combiner     = "OR"
  conditions {
    display_name = "Uptime check failing"
    condition_threshold {
      filter     = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.label.check_id=\"${google_monitoring_uptime_check_config.http_check.uptime_check_id}\""
      duration   = "60s"
      comparison = "COMPARISON_GT"
      threshold_value = 1
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}

resource "google_monitoring_alert_policy" "high_cpu_alert" {
  display_name = "Cloud Run High CPU Alert"
  combiner     = "OR"
  conditions {
    display_name = "CPU utilization above 80%"
    condition_threshold {
      filter     = "metric.type=\"run.googleapis.com/container/cpu/utilizations\" AND resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_v2_service.backend.name}\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.8
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}

resource "google_monitoring_alert_policy" "high_memory_alert" {
  display_name = "Cloud Run High Memory Alert"
  combiner     = "OR"
  conditions {
    display_name = "Memory utilization above 90%"
    condition_threshold {
      filter     = "metric.type=\"run.googleapis.com/container/memory/utilizations\" AND resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_v2_service.backend.name}\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.9
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}

resource "google_monitoring_alert_policy" "high_error_rate_alert" {
  display_name = "Cloud Run High Error Rate Alert"
  combiner     = "OR"
  conditions {
    display_name = "5xx error rate above 5%"
    condition_threshold {
      filter     = "metric.type=\"run.googleapis.com/request_count\" AND resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_v2_service.backend.name}\" AND metric.label.response_code_class=\"5xx\""
      duration   = "60s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.05
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}
