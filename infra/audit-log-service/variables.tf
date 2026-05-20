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

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "europe-central2-a"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "audit-log-service"
}

variable "image" {
  description = "Docker image to deploy"
  type        = string
}
