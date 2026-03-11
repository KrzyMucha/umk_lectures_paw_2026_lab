output "service_url" {
  description = "URL serwisu Cloud Run"
  value       = google_cloud_run_v2_service.offers_api.uri
}

output "image_path" {
  description = "Pełna ścieżka do obrazu w Artifact Registry"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.service_name}:latest"
}
