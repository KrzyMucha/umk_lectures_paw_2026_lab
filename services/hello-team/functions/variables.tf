variable "region" {
  description = "GCP region"
  type        = string
}

variable "functions_source_bucket" {
  description = "GCS bucket name containing function source zips"
  type        = string
}

variable "hello_source_object" {
  description = "GCS object name of the hello function source zip"
  type        = string
}
