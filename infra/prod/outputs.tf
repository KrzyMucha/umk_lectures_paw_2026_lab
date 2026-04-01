output "db_connection_name" {
  description = "Cloud SQL connection name for PROD"
  value       = google_sql_database_instance.this.connection_name
}

output "database_url" {
  description = "DATABASE_URL for PROD"
  value       = format("postgresql://%s:%s@%s:5432/%s?serverVersion=15.0&charset=utf8", google_sql_user.this.name, random_password.db_password.result, google_sql_database_instance.this.public_ip_address, google_sql_database.this.name)
  sensitive   = true
}
