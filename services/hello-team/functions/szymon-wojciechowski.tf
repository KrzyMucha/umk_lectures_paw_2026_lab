# Hello function for Szymon W
resource "google_cloudfunctions2_function" "hello_szymon_w" {
  name        = "hello-szymon-w"
  location    = var.region
  description = "Hello from Szymon W - Zespół 1"

  build_config {
    runtime     = "nodejs20"
    entry_point = "handler"
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.hello_source.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "128Mi"
    timeout_seconds    = 60
  }

  labels = {
    team   = "zespol-1"
    author = "szymon-w"
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "hello_szymon_w_public" {
  location = google_cloudfunctions2_function.hello_szymon_w.location
  name     = google_cloudfunctions2_function.hello_szymon_w.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output URL
output "hello_szymon_w_url" {
  value = google_cloudfunctions2_function.hello_szymon_w.service_config[0].uri
}