terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "functions_source" {
  name                        = "${var.project}-functions-source"
  location                    = var.region
  uniform_bucket_level_access = true
}

data "archive_file" "hello_source" {
  type        = "zip"
  source_dir  = "../services/hello-team/src/hello"
  output_path = "/tmp/hello-source.zip"
}

resource "google_storage_bucket_object" "hello_source" {
  name   = "hello-source-${data.archive_file.hello_source.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.hello_source.output_path
}

module "hello_functions" {
  source = "../services/hello-team/functions"

  region                  = var.region
  functions_source_bucket = google_storage_bucket.functions_source.name
  hello_source_object     = google_storage_bucket_object.hello_source.name
}