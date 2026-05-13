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

variable "db_instance_name" {
  description = "Cloud SQL DEV instance name"
  type        = string
  default     = "mini-allegro-db-dev"
}

variable "db_username" {
  description = "Database application username"
  type        = string
  default     = "app"
}

variable "db_name" {
  description = "DEV database name"
  type        = string
  default     = "mini_allegro_dev"
}
