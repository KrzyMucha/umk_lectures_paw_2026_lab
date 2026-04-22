variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "project-f5f4f6f0-acae-485b-a16"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-central2"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "offers-service-dev"
}

variable "image" {
  description = "Docker image to deploy"
  type        = string
}

variable "database_url" {
  description = "PostgreSQL connection URL"
  type        = string
  sensitive   = true
}
