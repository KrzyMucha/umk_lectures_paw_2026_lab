resource "google_cloud_run_v2_service" "offers_service" {
  name     = var.offers_service_name
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}/${var.offers_service_name}:latest"

      ports {
        container_port = 8082
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        startup_cpu_boost = true
      }

      env {
        name  = "PORT"
        value = "8082"
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service_iam_member" "offers_service_public_access" {
  location = google_cloud_run_v2_service.offers_service.location
  name     = google_cloud_run_v2_service.offers_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
