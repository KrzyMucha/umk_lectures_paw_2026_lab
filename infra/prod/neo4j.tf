# Neo4J Database on Compute Engine VM (PRODUCTION)
# Configured with Docker and persistent storage with higher specifications

variable "neo4j_instance_name" {
  description = "Neo4J Compute Engine instance name"
  type        = string
  default     = "mini-allegro-neo4j-prod"
}

variable "neo4j_machine_type" {
  description = "Compute Engine machine type for Neo4J"
  type        = string
  default     = "e2-standard-2"  # More powerful for prod
}

variable "neo4j_disk_size_gb" {
  description = "Persistent disk size for Neo4J"
  type        = number
  default     = 100  # Larger disk for prod
}

variable "neo4j_initial_password" {
  description = "Initial password for Neo4J admin user"
  type        = string
  sensitive   = true
}

# Random suffix for unique naming
resource "random_string" "neo4j_suffix" {
  length  = 4
  special = false
  upper   = false
}

# Service account for Neo4J VM
resource "google_service_account" "neo4j" {
  account_id   = "neo4j-prod-server"
  display_name = "Service account for Neo4J PROD server"
}

# Compute Engine persistent disk for Neo4J data (SSD for better performance)
resource "google_compute_disk" "neo4j_data" {
  name  = "neo4j-data-disk-prod-${random_string.neo4j_suffix.result}"
  type  = "pd-ssd"  # SSD for prod
  zone  = "${var.region}-a"
  size  = var.neo4j_disk_size_gb
}

# Compute Engine instance for Neo4J (PROD)
resource "google_compute_instance" "neo4j" {
  name         = "${var.neo4j_instance_name}-${random_string.neo4j_suffix.result}"
  machine_type = var.neo4j_machine_type
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "projects/debian-cloud/global/images/debian-12-bookworm-v20240213"
      size  = 30
    }
  }

  attached_disk {
    source      = google_compute_disk.neo4j_data.id
    device_name = "neo4j-data"
  }

  network_interface {
    network = "default"
    access_config {
      # Ephemeral public IP
    }
  }

  service_account {
    email  = google_service_account.neo4j.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    enable-oslogin = "true"
  }

  metadata_startup_script = base64encode(templatefile("${path.module}/neo4j-startup.sh", {
    neo4j_password = var.neo4j_initial_password
    neo4j_port     = "7687"
  }))

  tags = ["neo4j", "http-server", "https-server"]

  labels = {
    app = "mini-allegro"
    env = "prod"
  }

  depends_on = [
    google_compute_disk.neo4j_data
  ]
}

# Firewall rule for Neo4J bolt protocol (more restrictive for prod)
resource "google_compute_firewall" "neo4j_bolt" {
  name    = "allow-neo4j-bolt-prod"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["7687", "7474", "7473"]
  }

  source_ranges = ["0.0.0.0/0"]  # In production, restrict to Cloud Run IP ranges
  target_tags   = ["neo4j"]
}

# Output Neo4J connection info
output "neo4j_ip_address" {
  description = "Neo4J server public IP (PROD)"
  value       = google_compute_instance.neo4j.network_interface[0].access_config[0].nat_ip
}

output "neo4j_uri" {
  description = "Neo4J connection URI (PROD)"
  value       = "neo4j://${google_compute_instance.neo4j.network_interface[0].access_config[0].nat_ip}:7687"
}

output "neo4j_browser_url" {
  description = "Neo4J Browser URL (PROD)"
  value       = "http://${google_compute_instance.neo4j.network_interface[0].access_config[0].nat_ip}:7474/browser/"
}
