# Testy integracyjne - Krok 4d
# Wymaga uruchomionego monolitu (localhost:8080) i product-review-service (localhost:8081)

$env:APP_BASE_URL = "http://localhost:8080"

Write-Host "Uruchamiam testy integracyjne przeciwko $env:APP_BASE_URL..."
Write-Host ""

pytest
