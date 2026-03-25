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
  id = "projects/${var.project}/locations/${var.region}/repositories/mini-allegro"
  to = google_artifact_registry_repository.mini_allegro
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

resource "google_logging_metric" "cloud_run_error_count" {
  name        = "mini_allegro_cloud_run_error_count"
  description = "Counts ERROR and higher severity logs emitted by mini-allegro Cloud Run service"
  filter = join(" AND ", [
    "resource.type=\"cloud_run_revision\"",
    "resource.labels.service_name=\"${var.service_name}\"",
    "severity>=ERROR",
  ])
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "mini-allegro-alert-email"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "cloud_run_error_burst" {
  display_name = "mini-allegro Cloud Run error burst"
  combiner     = "OR"

  documentation {
    subject   = "[mini-allegro] 5+ ERROR logs in 5 minutes"
    mime_type = "text/markdown"
    content   = <<-EOT
      Wykryto nagromadzenie błędów aplikacji mini-allegro.

      **Warunek alertu:** więcej niż 4 logi o `severity>=ERROR` w 5 minut (czyli 5+ błędów).

      **Co sprawdzić od razu:**
      1. Cloud Logging -> Logs Explorer
      2. Użyj filtra:

      ```
      resource.type="cloud_run_revision"
      resource.labels.service_name="mini-allegro"
      severity>=ERROR
      ```

      **Uwaga:** mail alertowy z Cloud Monitoring nie dołącza pełnej listy treści logów; szczegółowy opis błędów jest w Cloud Logging.
    EOT
  }

  conditions {
    display_name = "5+ errors in 5 minutes"

    condition_threshold {
      filter = join(" AND ", [
        "metric.type=\"logging.googleapis.com/user/${google_logging_metric.cloud_run_error_count.name}\"",
        "resource.type=\"cloud_run_revision\"",
        "resource.labels.service_name=\"${var.service_name}\"",
      ])
      comparison      = "COMPARISON_GT"
      threshold_value = 4
      duration        = "0s"

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.labels.service_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  alert_strategy {
    auto_close = "1800s"
  }

  enabled = true
}
