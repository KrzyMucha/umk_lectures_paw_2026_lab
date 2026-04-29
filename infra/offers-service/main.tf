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

resource "google_storage_bucket" "offers_data" {
  name                        = "${var.project}-offers-data-${var.environment}"
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "google_cloud_run_v2_service" "offers_service" {
  name     = var.service_name
  location = var.region

  template {
    volumes {
      name = "offers-storage"

      gcs {
        bucket    = google_storage_bucket.offers_data.name
        read_only = false
      }
    }

    containers {
      image = var.image

      ports {
        container_port = 8082
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }

      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }

      env {
        name  = "STORAGE_MOUNT_PATH"
        value = var.storage_mount_path
      }

      volume_mounts {
        name       = "offers-storage"
        mount_path = var.storage_mount_path
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
