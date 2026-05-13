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

# --- Elasticsearch VM ---

resource "google_compute_instance" "elasticsearch" {
  name         = "elasticsearch-vm"
  machine_type = "e2-standard-2"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 50
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  tags = ["elasticsearch"]

  service_account {
    scopes = ["cloud-platform"]
  }

  metadata = {
    startup-script = <<-STARTUP
      #!/bin/bash
      set -e

      # Java
      apt-get update -y
      apt-get install -y openjdk-17-jre-headless curl gnupg

      # Elasticsearch repo
      wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch \
        | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
      echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] \
        https://artifacts.elastic.co/packages/8.x/apt stable main" \
        | tee /etc/apt/sources.list.d/elastic-8.x.list
      apt-get update -y
      apt-get install -y elasticsearch

      # Konfiguracja ES
      cat > /etc/elasticsearch/elasticsearch.yml <<EOF
      network.host: 0.0.0.0
      discovery.type: single-node
      xpack.security.enabled: false
      EOF

      systemctl enable elasticsearch
      systemctl start elasticsearch

      # Skrypt idle shutdown
      cat > /usr/local/bin/idle-shutdown.sh <<'SCRIPT'
      #!/bin/bash
      PREV_INDEX=0
      PREV_SEARCH=0
      IDLE_MINUTES=0

      while true; do
          sleep 300

          CURR_INDEX=$(curl -s http://localhost:9200/_stats/indexing 2>/dev/null \
            | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['_all']['total']['indexing']['index_total'])" \
            2>/dev/null || echo "$PREV_INDEX")

          CURR_SEARCH=$(curl -s http://localhost:9200/_stats/search 2>/dev/null \
            | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['_all']['total']['search']['query_total'])" \
            2>/dev/null || echo "$PREV_SEARCH")

          if [ "$CURR_INDEX" = "$PREV_INDEX" ] && [ "$CURR_SEARCH" = "$PREV_SEARCH" ]; then
              IDLE_MINUTES=$((IDLE_MINUTES + 5))
          else
              IDLE_MINUTES=0
              PREV_INDEX=$CURR_INDEX
              PREV_SEARCH=$CURR_SEARCH
          fi

          if [ "$IDLE_MINUTES" -ge 30 ]; then
              ZONE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" \
                -H "Metadata-Flavor: Google" | cut -d/ -f4)
              NAME=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/name" \
                -H "Metadata-Flavor: Google")
              gcloud compute instances stop "$NAME" --zone="$ZONE" --quiet
          fi
      done
      SCRIPT

      chmod +x /usr/local/bin/idle-shutdown.sh
      nohup /usr/local/bin/idle-shutdown.sh >> /var/log/idle-shutdown.log 2>&1 &
    STARTUP
  }
}

# Firewall — port 9200 dostępny tylko z Cloud Run (publiczne IP GCP)
resource "google_compute_firewall" "elasticsearch" {
  name    = "allow-elasticsearch"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["9200"]
  }

  target_tags   = ["elasticsearch"]
  source_ranges = ["0.0.0.0/0"]
}

# --- Cloud Run: audit-log-service ---

resource "google_cloud_run_v2_service" "audit_log_service" {
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

      env {
        name  = "ELASTICSEARCH_URL"
        value = "http://${google_compute_instance.elasticsearch.network_interface[0].access_config[0].nat_ip}:9200"
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.audit_log_service.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
