# Hello function for Szymon
resource "google_cloudfunctions2_function" "hello_szymon_falkowski" {
  name        = "hello-szymon"
  location    = var.region
  description = "Hello from Szymon - Zespół 1"

  build_config {
    runtime     = "nodejs20"
    entry_point = "handler"
    source {
      storage_source {
        bucket = var.bucket
        object = var.object
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
    author = "szymon"
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "hello_szymon_public" {
  location = google_cloudfunctions2_function.hello_szymon_falkowski.location
  name     = google_cloudfunctions2_function.hello_szymon_falkowski.name
  role     = "roles/run.invoker"
  member   = "allUsers"

}

# Output URL
output "hello_szymon_url" {
  value = google_cloudfunctions2_function.hello_szymon_falkowski.service_config[0].uri
}
