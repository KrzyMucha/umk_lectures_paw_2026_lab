output "topic_name" {
  description = "Pub/Sub topic name for service logs"
  value       = google_pubsub_topic.service_logs.name
}

output "topic_id" {
  description = "Pub/Sub topic full resource ID"
  value       = google_pubsub_topic.service_logs.id
}

output "subscription_name" {
  description = "Pub/Sub pull subscription name"
  value       = google_pubsub_subscription.service_logs_pull.name
}
