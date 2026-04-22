terraform {
  required_version = ">= 1.0"
  backend "gcs" {}
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

resource "google_cloud_run_v2_service" "offers_service" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image

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
        name  = "DATABASE_URL"
        value = var.database_url
      }

      env {
        name  = "PORT"
        value = "8082"
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.offers_service.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
