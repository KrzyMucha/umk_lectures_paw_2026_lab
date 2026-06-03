variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "paw-2026-496213"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-central2"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "embedding-service-dev"
}

variable "image" {
  description = "Docker image to deploy"
  type        = string
}

variable "qdrant_machine_type" {
  description = "GCE machine type for the Qdrant VM"
  type        = string
  default     = "e2-medium"
}
