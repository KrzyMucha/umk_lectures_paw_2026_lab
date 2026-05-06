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

variable "neo4j_uri" {
  description = "Neo4J connection URI for user-service"
  type        = string
  sensitive   = true
}

variable "neo4j_username" {
  description = "Neo4J username"
  type        = string
  default     = "neo4j"
  sensitive   = true
}

variable "neo4j_password" {
  description = "Neo4J password for user-service"
  type        = string
  sensitive   = true
}
