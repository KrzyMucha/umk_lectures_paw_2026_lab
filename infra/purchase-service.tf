locals {
  purchase_service_name = "purchase-service-dev"
  purchase_image        = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}/purchase-service:latest"
}

resource "google_cloud_run_v2_service" "purchase_service" {
  name     = local.purchase_service_name
  location = var.region

  template {
    containers {
      image = local.purchase_image

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

# NOTE: IAM permissions for Cloud Run disabled due to insufficient permissions on falkowskisz01@gmail.com
# To enable, grant run.services.setIamPolicy permission or manually set IAM using gcloud:
# gcloud run services add-iam-policy-binding purchase-service-dev \
#   --region=europe-central2 \
#   --member=allUsers \
#   --role=roles/run.invoker \
#   --project=paw-2026-496213
# resource "google_cloud_run_v2_service_iam_member" "purchase_service_public_access" {
#   location = google_cloud_run_v2_service.purchase_service.location
#   name     = google_cloud_run_v2_service.purchase_service.name
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }

output "purchase_service_url" {
  description = "URL of purchase-service Cloud Run service"
  value       = google_cloud_run_v2_service.purchase_service.uri
}
