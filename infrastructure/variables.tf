variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "project-f5f4f6f0-acae-485b-a16"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-central2"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "symfony-offers"
}

variable "app_secret" {
  description = "Symfony APP_SECRET value"
  type        = string
}

variable "offer_service_url" {
  description = "Upstream service URL used by the monolith"
  type        = string
}