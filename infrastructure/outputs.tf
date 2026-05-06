output "service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.symfony_offers.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.symfony_offers.repository_id}"
}

output "purchase_service_url" {
  description = "URL of the deployed purchase Cloud Run service"
  value       = google_cloud_run_v2_service.symfony_purchase.uri
}

output "purchase_artifact_registry_repository" {
  description = "Artifact Registry repository URL for purchase"
  value       = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.symfony_purchase.repository_id}"
}