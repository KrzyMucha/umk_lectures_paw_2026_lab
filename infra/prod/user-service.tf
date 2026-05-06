# User Service Cloud Run for PROD
# FastAPI + Neo4J (Production-grade configuration)

variable "user_service_image_name" {
  description = "Docker image name for user-service"
  type        = string
  default     = "user-service"
}

# Reference artifact registry (shared across dev/prod)
data "google_artifact_registry_repository" "mini_allegro" {
  location      = var.region
  repository_id = "mini-allegro"
}

# Cloud Run service for user-service-prod
resource "google_cloud_run_v2_service" "user_service_prod" {
  name     = "user-service-prod"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${data.google_artifact_registry_repository.mini_allegro.repository_id}/${var.user_service_image_name}:latest"

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
        name  = "NEO4J_URI"
        value = "neo4j://${google_compute_instance.neo4j.network_interface[0].access_config[0].nat_ip}:7687"
      }

      env {
        name  = "NEO4J_USERNAME"
        value = var.neo4j_username
      }

      env {
        name  = "NEO4J_PASSWORD"
        value = var.neo4j_password
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public access to user-service-prod
resource "google_cloud_run_v2_service_iam_member" "user_service_public_access" {
  location = google_cloud_run_v2_service.user_service_prod.location
  name     = google_cloud_run_v2_service.user_service_prod.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "user_service_prod_url" {
  description = "URL for user-service-prod"
  value       = google_cloud_run_v2_service.user_service_prod.uri
}

output "user_service_prod_image" {
  description = "Docker image URI for user-service"
  value       = "${var.region}-docker.pkg.dev/${var.project}/${data.google_artifact_registry_repository.mini_allegro.repository_id}/${var.user_service_image_name}"
}
