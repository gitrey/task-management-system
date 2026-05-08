resource "google_monitoring_alert_policy" "gke_high_cpu_alert" {
  display_name = "GKE Container High CPU Alert"
  combiner     = "OR"
  conditions {
    display_name = "CPU utilization above 80%"
    condition_threshold {
      filter     = "metric.type=\"kubernetes.io/container/cpu/core_usage_time\" AND resource.type=\"k8s_container\" AND resource.label.container_name=\"task-mgmt-backend\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.8
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}

resource "google_monitoring_alert_policy" "gke_high_memory_alert" {
  display_name = "GKE Container High Memory Alert"
  combiner     = "OR"
  conditions {
    display_name = "Memory utilization above 90%"
    condition_threshold {
      filter     = "metric.type=\"kubernetes.io/container/memory/used_bytes\" AND resource.type=\"k8s_container\" AND resource.label.container_name=\"task-mgmt-backend\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 460800000 # 90% of 512Mi approx
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}

resource "google_monitoring_alert_policy" "gke_restart_alert" {
  display_name = "GKE Container Restart Alert"
  combiner     = "OR"
  conditions {
    display_name = "Container restarts in last 5m"
    condition_threshold {
      filter     = "metric.type=\"kubernetes.io/container/restart_count\" AND resource.type=\"k8s_container\" AND resource.label.container_name=\"task-mgmt-backend\""
      duration   = "60s"
      comparison = "COMPARISON_GT"
      threshold_value = 0
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_DELTA"
      }
    }
  }

  notification_channels = [var.notification_channel_id]
}
