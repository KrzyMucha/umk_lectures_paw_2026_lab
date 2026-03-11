variable "region" {
  description = "GCP region"
  type        = string
}

variable "functions_source_bucket" {
  description = "GCS bucket name with function source"
  type        = string
}

variable "hello_source_object" {
  description = "GCS object name of the hello source zip"
  type        = string
}