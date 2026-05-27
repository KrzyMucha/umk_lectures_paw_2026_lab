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

resource "google_project_service" "apikeys" {
  service            = "apikeys.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "generativelanguage" {
  service            = "generativelanguage.googleapis.com"
  disable_on_destroy = false
}

resource "google_apikeys_key" "gemini" {
  name         = "embedding-service-gemini-key"
  display_name = "embedding-service-gemini-key"
  project      = var.project

  restrictions {
    api_targets {
      service = "generativelanguage.googleapis.com"
    }
  }

  depends_on = [
    google_project_service.apikeys,
    google_project_service.generativelanguage,
  ]
}

# --- Qdrant on GCE VM ---

resource "google_compute_address" "qdrant" {
  name   = "qdrant-dev-ip"
  region = var.region
}

resource "google_compute_instance" "qdrant" {
  name         = "qdrant-dev"
  machine_type = var.qdrant_machine_type
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 20
    }
  }

  network_interface {
    network = "default"

    access_config {
      nat_ip = google_compute_address.qdrant.address
    }
  }

  tags = ["qdrant"]

  metadata_startup_script = <<-'EOT'
    #!/bin/bash
    set -e

    # Install Docker (idempotent)
    if ! command -v docker &>/dev/null; then
      apt-get update -qq
      apt-get install -y docker.io
      systemctl enable --now docker
    fi

    # Start existing Qdrant container or create a new one
    docker start qdrant 2>/dev/null || \
      docker run -d --restart=always --name qdrant \
        -p 6333:6333 -p 6334:6334 \
        -v /qdrant_storage:/qdrant/storage \
        qdrant/qdrant:latest

    # Idle watchdog — shutdown after 10 min with zero connections
    cat > /usr/local/bin/idle-watchdog.sh << 'SCRIPT'
    #!/bin/bash
    IDLE_TIMEOUT=600
    LAST_ACTIVITY=$(date +%s)

    while true; do
      CONNS=$(ss -tn state established '( dport = :6333 or sport = :6333 )' | tail -n +2 | wc -l)
      if [ "$CONNS" -gt 0 ]; then
        LAST_ACTIVITY=$(date +%s)
      fi

      NOW=$(date +%s)
      if [ $((NOW - LAST_ACTIVITY)) -ge $IDLE_TIMEOUT ]; then
        shutdown -h now
        exit 0
      fi

      sleep 60
    done
    SCRIPT
    chmod +x /usr/local/bin/idle-watchdog.sh

    # Run watchdog if not already running
    pgrep -f idle-watchdog.sh >/dev/null || nohup /usr/local/bin/idle-watchdog.sh &>/dev/null &
  EOT
}

resource "google_compute_firewall" "qdrant" {
  name    = "allow-qdrant"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["6333", "6334"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["qdrant"]
}

# --- Cloud Run: embedding-service ---

resource "google_cloud_run_v2_service" "embedding_service" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      env {
        name  = "PORT"
        value = "8080"
      }

      env {
        name  = "GEMINI_API_KEY"
        value = google_apikeys_key.gemini.key_string
      }

      env {
        name  = "QDRANT_URL"
        value = "http://${google_compute_address.qdrant.address}:6333"
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
