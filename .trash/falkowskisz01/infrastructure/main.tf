provider "google" {
  project = var.project
  region  = var.region
}

# Source bucket
resource "google_storage_bucket" "functions_source" {
  name                        = "${var.project}-functions-szymon"
  location                    = var.region
  uniform_bucket_level_access = true
}

# Zip the function source
data "archive_file" "hello_source" {
  type        = "zip"
  source_dir  = "${path.module}/../services/hello-team/src/hello"
  output_path = "${path.module}/hello-source.zip"
}

# Upload zipped source to bucket
resource "google_storage_bucket_object" "hello_source" {
  name   = "hello-source-${data.archive_file.hello_source.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.hello_source.output_path
}

# Call the functions module
module "hello_team_functions" {
  source = "../services/hello-team/functions"
  
  region = var.region
  bucket = google_storage_bucket.functions_source.name
  object = google_storage_bucket_object.hello_source.name
}
