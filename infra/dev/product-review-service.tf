import {
  id = "projects/project-f5f4f6f0-acae-485b-a16/locations/europe-central2/services/product-review-service-dev"
  to = google_cloud_run_v2_service.product_review_service
}

resource "google_cloud_run_v2_service" "product_review_service" {
  name     = "product-review-service-dev"
  location = var.region

  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello:latest"

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
        value = "dev"
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service_iam_member" "product_review_service_public" {
  location = google_cloud_run_v2_service.product_review_service.location
  name     = google_cloud_run_v2_service.product_review_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
