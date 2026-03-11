# Hello function for {Imię}
resource "google_cloudfunctions2_function" "hello_{szymon}" {
  name        = "hello-{Szymon}"
  location    = var.region
  description = "Hello from {Szymon} - Zespół {N}"

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
    team   = "zespol-{n}"
    author = "{imie}"
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "hello_{imie}_public" {
  location = google_cloudfunctions2_function.hello_{imie}.location
  name     = google_cloudfunctions2_function.hello_{imie}.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output URL
output "hello_{imie}_url" {
  value = google_cloudfunctions2_function.hello_{imie}.service_config[0].uri
}