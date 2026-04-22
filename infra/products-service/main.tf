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

resource "google_cloud_run_v2_service" "products_service" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image

      ports {
        container_port = 8081
      }

<<<<<<< HEAD
      env {
        name  = "PORT"
        value = "8081"
      }

=======
>>>>>>> 2ebfdb3 (workflow and infra for product service)
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.products_service.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
