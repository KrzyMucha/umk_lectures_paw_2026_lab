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

# Firestore (Native mode) — baza danych dla product-review-service.
# Importowana bo zostala stworzona recznie przed dodaniem do Terraform.
import {
  id = "projects/${var.project}/databases/(default)"
  to = google_firestore_database.default
}

resource "google_firestore_database" "default" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Cloud Run domyslnie uzywa service account: PROJECT_NUMBER-compute@developer.gserviceaccount.com
# Nadajemy mu dostep do Firestore
data "google_project" "project" {}

resource "google_project_iam_member" "cloud_run_firestore" {
  project = var.project
  role    = "roles/datastore.user"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

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
