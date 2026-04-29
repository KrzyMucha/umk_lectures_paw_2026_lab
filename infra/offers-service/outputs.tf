output "service_url" {
  description = "URL of the deployed offers-service Cloud Run service"
  value       = google_cloud_run_v2_service.offers_service.uri
}

output "storage_bucket_name" {
  description = "Name of the GCS bucket mounted as persistent storage"
  value       = google_storage_bucket.offers_data.name
}

output "storage_mount_path" {
  description = "Mount path of the GCS volume inside the container"
  value       = var.storage_mount_path
}
