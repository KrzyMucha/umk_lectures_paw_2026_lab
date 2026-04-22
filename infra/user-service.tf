resource "google_cloud_run_v2_service" "user_service_dev" {
  name     = var.user_service_dev_name
  location = var.region

  template {
    service_account = google_service_account.user_service_dev.email

    containers {
      image = "europe-central2-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}/user-service:latest"

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
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.user_service_dev_database_url.secret_id
            version = "latest"
          }
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.dev.connection_name]
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

resource "google_cloud_run_v2_service_iam_member" "user_service_dev_public_access" {
  location = google_cloud_run_v2_service.user_service_dev.location
  name     = google_cloud_run_v2_service.user_service_dev.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service" "user_service_prod" {
  name     = var.user_service_prod_name
  location = var.region

  template {
    service_account = google_service_account.user_service_prod.email

    containers {
      image = "europe-central2-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.mini_allegro.repository_id}/user-service:latest"

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
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.user_service_prod_database_url.secret_id
            version = "latest"
          }
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.prod.connection_name]
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

resource "google_cloud_run_v2_service_iam_member" "user_service_prod_public_access" {
  location = google_cloud_run_v2_service.user_service_prod.location
  name     = google_cloud_run_v2_service.user_service_prod.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
