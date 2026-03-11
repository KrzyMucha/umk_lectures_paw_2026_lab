resource "google_cloudfunctions2_function" "hello_lukasz" {
  name        = "hello-lukasz"
  location    = var.region
  description = "Hello from Lukasz - Zespół 1"

  build_config {
    runtime     = "nodejs22"
    entry_point = "helloHttp"
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
    author = "lukasz"
  }
}

resource "google_cloud_run_v2_service_iam_member" "hello_lukasz_public" {
  location = google_cloudfunctions2_function.hello_lukasz.location
  name     = google_cloudfunctions2_function.hello_lukasz.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "hello_lukasz_url" {
  value = google_cloudfunctions2_function.hello_lukasz.service_config[0].uri
}