output "service_url" {
  description = "URL of the deployed products-service Cloud Run service"
  value       = google_cloud_run_v2_service.products_service.uri
}
