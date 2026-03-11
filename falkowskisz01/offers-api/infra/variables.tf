variable "project_id" {
  description = "ID projektu Google Cloud"
  type        = string
  # Ustaw przez: terraform apply -var='project_id=twoj-projekt-id'
  # lub w pliku terraform.tfvars
}

variable "region" {
  description = "Region GCP"
  type        = string
  default     = "us-central1"
}

variable "repository_name" {
  description = "Nazwa repozytorium Artifact Registry"
  type        = string
  default     = "offers-repo"
}

variable "service_name" {
  description = "Nazwa serwisu Cloud Run"
  type        = string
  default     = "offers-api"
}
