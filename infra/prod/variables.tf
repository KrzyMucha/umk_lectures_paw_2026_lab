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
  description = "Cloud SQL PROD instance name"
  type        = string
  default     = "mini-allegro-db-prod"
}

variable "db_username" {
  description = "Database application username"
  type        = string
  default     = "app"
}

variable "db_name" {
  description = "PROD database name"
  type        = string
  default     = "mini_allegro_prod"
}

variable "neo4j_initial_password" {
  description = "Initial password for Neo4J admin user"
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
