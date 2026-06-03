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


# NOTE: IAM on project level is intentionally managed outside this Terraform root.
# This avoids 403 (Policy update access denied) for users/CI without project IAM admin rights.
# If needed, grant Firestore access manually to the Cloud Run runtime service account.


resource "google_cloud_run_v2_service" "product_review_service" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image

      ports {
        container_port = 8080
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

resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.product_review_service.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
