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

      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }
}

# NOTE: IAM permissions disabled due to insufficient permissions on the service account.
# Set manually using gcloud:
# gcloud run services add-iam-policy-binding products-service-dev \
#   --region=europe-central2 \
#   --member=allUsers \
#   --role=roles/run.invoker \
#   --project=paw-2026-496213
# resource "google_cloud_run_v2_service_iam_member" "public" {
#   name     = google_cloud_run_v2_service.products_service.name
#   location = var.region
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }
