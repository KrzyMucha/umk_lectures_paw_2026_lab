terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

resource "google_artifact_registry_repository" "symfony_offers" {
  repository_id = "symfony-offers"
  location      = var.region
  format        = "DOCKER"
  description   = "Docker images for symfony-offers app"
}

resource "google_cloud_run_v2_service" "symfony_offers" {
  name                = var.service_name
  location            = var.region
  deletion_protection = false

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.symfony_offers.repository_id}/${var.service_name}:latest"

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
        name  = "APP_ENV"
        value = "prod"
      }

      env {
        name  = "APP_SECRET"
        value = var.app_secret
      }

      env {
        name  = "OFFER_SERVICE_URL"
        value = var.offer_service_url
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

resource "google_cloud_run_v2_service_iam_member" "symfony_offers_public" {
  location = google_cloud_run_v2_service.symfony_offers.location
  name     = google_cloud_run_v2_service.symfony_offers.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}