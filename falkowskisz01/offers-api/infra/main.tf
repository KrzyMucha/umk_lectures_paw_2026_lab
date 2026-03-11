terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -------------------------------------------------------
# Artifact Registry - repozytorium obrazów Docker
# -------------------------------------------------------
resource "google_artifact_registry_repository" "offers" {
  repository_id = var.repository_name
  location      = var.region
  format        = "DOCKER"
  description   = "Offers API Docker images"
}

# -------------------------------------------------------
# Cloud Run - serwis aplikacji
# -------------------------------------------------------
resource "google_cloud_run_v2_service" "offers_api" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.service_name}:latest"

      ports {
        container_port = 8080
      }

      env {
        name  = "APP_ENV"
        value = "prod"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  depends_on = [google_artifact_registry_repository.offers]
}

# -------------------------------------------------------
# Publiczny dostęp (bez uwierzytelniania)
# -------------------------------------------------------
resource "google_cloud_run_v2_service_iam_member" "public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.offers_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
