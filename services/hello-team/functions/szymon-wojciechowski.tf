# Hello function for Szymon Wojciechowski
resource "google_cloudfunctions2_function" "hello_szymon_wojciechowski" {
  name        = "hello-szymon-wojciechowski"
  location    = var.region
  description = "Hello from Szymon Wojciechowski - Zespół 1"

  build_config {
    runtime     = "nodejs20"
    entry_point = "handler"
    source {
      storage_source {
        bucket = var.functions_source_bucket
        object = var.hello_source_object
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
    author = "szymon-wojciechowski"
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "hello_szymon_wojciechowski_public" {
  location = google_cloudfunctions2_function.hello_szymon_wojciechowski.location
  name     = google_cloudfunctions2_function.hello_szymon_wojciechowski.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output URL
output "hello_szymon_wojciechowski_url" {
  value = google_cloudfunctions2_function.hello_szymon_wojciechowski.service_config[0].uri
}