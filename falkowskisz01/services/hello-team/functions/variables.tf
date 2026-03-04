variable "region" {
  type        = string
  description = "GCP Region for the functions"
  default     = "europe-central2"
}

variable "bucket" {
  type        = string
  description = "Bucket containing function source"
  default     = "paw-2026-functions-source"
}

variable "object" {
  type        = string
  description = "Object name of function source zip"
  default     = "hello-source.zip"
}
