locals {
  offer_service_name = "offer-service-dev"
  offer_image        = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}/offer-service:latest"
}

resource "google_cloud_run_v2_service" "offer_service" {
  name     = local.offer_service_name
  location = var.region

  template {
    containers {
      image = local.offer_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }

      env {
        name  = "PORT"
        value = "8080"
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

resource "google_cloud_run_v2_service_iam_member" "offer_public_access" {
  location = google_cloud_run_v2_service.offer_service.location
  name     = google_cloud_run_v2_service.offer_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "offer_service_url" {
  description = "URL of offer-service Cloud Run service"
  value       = google_cloud_run_v2_service.offer_service.uri
}