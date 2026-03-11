# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "symfony_offers" {
  location      = var.region
  repository_id = "symfony-offers"
  format        = "DOCKER"
  description   = "Docker images for symfony-offers app"
}

# Cloud Run service
resource "google_cloud_run_v2_service" "symfony_offers" {
  name     = "symfony-offers"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/symfony-offers/app:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "APP_ENV"
        value = "prod"
      }

      env {
        name  = "APP_DEBUG"
        value = "0"
      }

      env {
        name  = "APP_SECRET"
        value = var.app_secret
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "symfony_offers_public" {
  location = google_cloud_run_v2_service.symfony_offers.location
  name     = google_cloud_run_v2_service.symfony_offers.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "symfony_offers_url" {
  value = google_cloud_run_v2_service.symfony_offers.uri
}
