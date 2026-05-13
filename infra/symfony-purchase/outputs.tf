output "service_url" {
  description = "URL of the deployed symfony-purchase Cloud Run service"
  value       = google_cloud_run_v2_service.symfony_purchase.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL for symfony-purchase"
  value       = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.symfony_purchase.repository_id}"
}
