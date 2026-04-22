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
  default     = "mini-allegro"
}

variable "alert_email" {
  description = "Email for Cloud Monitoring alert notifications"
  type        = string
}

variable "db_dev_instance_name" {
  description = "Cloud SQL DEV instance name"
  type        = string
  default     = "mini-allegro-db-dev"
}

variable "db_prod_instance_name" {
  description = "Cloud SQL PROD instance name"
  type        = string
  default     = "mini-allegro-db-prod"
}

variable "db_username" {
  description = "Database application username"
  type        = string
  default     = "app"
}

variable "db_dev_name" {
  description = "DEV database name"
  type        = string
  default     = "mini_allegro_dev"
}

variable "db_prod_name" {
  description = "PROD database name"
  type        = string
  default     = "mini_allegro_prod"
}

variable "user_service_dev_name" {
  description = "Cloud Run service name for DEV user-service"
  type        = string
  default     = "user-service-dev"
}

variable "user_service_prod_name" {
  description = "Cloud Run service name for PROD user-service"
  type        = string
  default     = "user-service-prod"
}

variable "user_service_target" {
  description = "Which user-service URL should be injected into mini-allegro (dev|prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "prod"], var.user_service_target)
    error_message = "user_service_target must be one of: dev, prod"
  }
}
