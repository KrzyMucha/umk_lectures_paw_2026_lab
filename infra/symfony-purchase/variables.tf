variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "paw-2026-496213"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-central2"
}

variable "purchase_service_name" {
  description = "Cloud Run service name for symfony-purchase"
  type        = string
  default     = "symfony-purchase"
}

variable "app_secret" {
  description = "Symfony APP_SECRET value"
  type        = string
}

variable "purchase_service_url" {
  description = "Upstream purchase-service (Python) URL"
  type        = string
}
