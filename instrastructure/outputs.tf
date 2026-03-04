output "functions_source_bucket" {
  description = "Name of the GCS bucket storing function source zips"
  value       = google_storage_bucket.functions_source.name
}

output "hello_source_object" {
  description = "GCS object name of the hello function source zip"
  value       = google_storage_bucket_object.hello_source.name
}

output "hello_szymon_orzechowski_url" {
  description = "URL of the hello-szymon-orzechowski Cloud Function"
  value       = module.hello_functions.hello_szymon_orzechowski_url
}
