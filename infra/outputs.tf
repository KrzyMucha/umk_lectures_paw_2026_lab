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

output "dev_db_connection_name" {
  description = "Cloud SQL connection name for DEV"
  value       = google_sql_database_instance.dev.connection_name
}

output "prod_db_connection_name" {
  description = "Cloud SQL connection name for PROD"
  value       = google_sql_database_instance.prod.connection_name
}

output "dev_database_url" {
  description = "DATABASE_URL for DEV"
  value       = format("postgresql://%s:%s@%s:5432/%s?serverVersion=15&charset=utf8", google_sql_user.dev.name, random_password.db_dev_password.result, google_sql_database_instance.dev.public_ip_address, google_sql_database.dev.name)
  sensitive   = true
}

output "prod_database_url" {
  description = "DATABASE_URL for PROD"
  value       = format("postgresql://%s:%s@%s:5432/%s?serverVersion=15&charset=utf8", google_sql_user.prod.name, random_password.db_prod_password.result, google_sql_database_instance.prod.public_ip_address, google_sql_database.prod.name)
  sensitive   = true
}
