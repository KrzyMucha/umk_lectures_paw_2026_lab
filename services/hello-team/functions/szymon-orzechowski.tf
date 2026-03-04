# Hello function for {Imię}
resource "google_cloudfunctions2_function" "hello_szymon_orzechowski" {
  name        = "hello-szymon-orzechowski"
  location    = var.region
  description = "Hello from Szymon Orzechowski - Zespół R"

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
    team   = "zespol-r"
    author = "szymon-orzechowski"
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "hello_szymon_orzechowski_public" {
  location = google_cloudfunctions2_function.hello_szymon_orzechowski.location
  name     = google_cloudfunctions2_function.hello_szymon_orzechowski.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output URL
output "hello_szymon_orzechowski_url" {
  value = google_cloudfunctions2_function.hello_szymon_orzechowski.service_config[0].uri
}