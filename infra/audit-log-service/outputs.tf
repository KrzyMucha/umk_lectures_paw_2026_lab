output "elasticsearch_ip" {
  description = "External IP of Elasticsearch VM"
  value       = google_compute_instance.elasticsearch.network_interface[0].access_config[0].nat_ip
}

output "audit_log_service_url" {
  description = "Cloud Run URL of audit-log-service"
  value       = google_cloud_run_v2_service.audit_log_service.uri
}
