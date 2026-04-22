output "service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.product_review_service.uri
}
