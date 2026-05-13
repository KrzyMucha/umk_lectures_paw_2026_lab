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

data "google_project" "project" {}

resource "google_pubsub_schema" "service_logs" {
  name = "mini-allegro-service-logs-schema"
  type = "PROTOCOL_BUFFER"
  definition = <<-PROTO
    syntax = "proto3";
    message ServiceLog {
      string timestamp = 1;
      string entity    = 2;
      string operation = 3;
      string payload   = 4;
      string endpoint  = 5;
    }
  PROTO
}

resource "google_pubsub_topic" "service_logs" {
  name = "mini-allegro-service-logs"

  depends_on = [google_pubsub_schema.service_logs]

  schema_settings {
    schema   = google_pubsub_schema.service_logs.id
    encoding = "JSON"
  }

  message_retention_duration = "604800s" # 7 days
}

resource "google_pubsub_subscription" "service_logs_pull" {
  name  = "mini-allegro-service-logs-pull"
  topic = google_pubsub_topic.service_logs.id

  ack_deadline_seconds       = 600
  message_retention_duration = "604800s" # 7 days

  expiration_policy {
    ttl = "" # never expires
  }
}

resource "google_project_iam_member" "cloud_run_pubsub_publisher" {
  project = var.project
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}
