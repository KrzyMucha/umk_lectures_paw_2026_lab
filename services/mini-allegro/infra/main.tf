terraform {
  required_version = ">= 1.0"
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

resource "google_artifact_registry_repository" "mini_allegro" {
  repository_id = "mini-allegro"
  location      = var.region
  format        = "DOCKER"
  description   = "Docker repository for mini-allegro"
}

import {
  id = "projects/${var.project}/locations/${var.region}/services/${var.service_name}"
  to = google_cloud_run_v2_service.mini_allegro
}

resource "google_cloud_run_v2_service" "mini_allegro" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}/${var.service_name}:latest"

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

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.mini_allegro.location
  name     = google_cloud_run_v2_service.mini_allegro.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
