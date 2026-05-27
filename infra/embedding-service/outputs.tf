output "service_url" {
  description = "URL of the deployed embedding-service"
  value       = google_cloud_run_v2_service.embedding_service.uri
}

output "gemini_api_key" {
  description = "Gemini API key (restricted to generativelanguage API)"
  value       = google_apikeys_key.gemini.key_string
  sensitive   = true
}

output "qdrant_instance_name" {
  description = "Name of the Qdrant GCE VM"
  value       = google_compute_instance.qdrant.name
}

output "qdrant_external_ip" {
  description = "Static external IP of the Qdrant VM"
  value       = google_compute_address.qdrant.address
}
