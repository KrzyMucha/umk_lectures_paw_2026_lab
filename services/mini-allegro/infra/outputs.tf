output "service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.mini_allegro.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}"
}

output "cloud_run_error_metric" {
  description = "Cloud Logging metric name for Cloud Run errors"
  value       = google_logging_metric.cloud_run_error_count.name
}

output "cloud_run_error_alert_policy" {
  description = "Cloud Monitoring alert policy name for Cloud Run error bursts"
  value       = google_monitoring_alert_policy.cloud_run_error_burst.name
}
