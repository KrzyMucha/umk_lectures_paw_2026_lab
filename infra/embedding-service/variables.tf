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

variable "qdrant_collection" {
  description = "Qdrant collection the service reads from (pre-populated, read-only)"
  type        = string
  default     = "ai-arxiv"
}

variable "ollama_model" {
  description = "Ollama embedding model, matching the 'nomic-embed-text' named vector"
  type        = string
  default     = "nomic-embed-text"
}

variable "gemini_model" {
  description = "Gemini embedding model used for the 'gemini-embedding-2' named vector"
  type        = string
  default     = "gemini-embedding-001"
}

variable "gemini_dim" {
  description = "Output dimensionality for the Gemini embedding (matches the collection's gemini-embedding-2 vector size)"
  type        = number
  default     = 3072
}
