# Test lokalny - Krok 4c
# Sprawdza czy monolit deleguje do product-review-service i czy odpowiedzi są identyczne.
#
# Przed uruchomieniem tego skryptu upewnij sie ze:
#   Terminal 1: cd services/product-review-service && .\run-local.ps1
#   Terminal 2: cd services/symphony-monolith && docker compose -f docker/docker-compose.yml up

$MONOLITH_URL = "http://localhost:8080"
$SERVICE_URL  = "http://localhost:8081"
$ENDPOINT     = "/product-reviews"

Write-Host ""
Write-Host "=== Test 4c: delegacja product-reviews ==="
Write-Host ""

Write-Host "--- Odpowiedz monolitu ($MONOLITH_URL$ENDPOINT) ---"
$monolithResponse = Invoke-RestMethod -Uri "$MONOLITH_URL$ENDPOINT" -Method GET
$monolithJson = $monolithResponse | ConvertTo-Json -Depth 10
Write-Host $monolithJson

Write-Host ""
Write-Host "--- Odpowiedz product-review-service ($SERVICE_URL$ENDPOINT) ---"
$serviceResponse = Invoke-RestMethod -Uri "$SERVICE_URL$ENDPOINT" -Method GET
$serviceJson = $serviceResponse | ConvertTo-Json -Depth 10
Write-Host $serviceJson

Write-Host ""
if ($monolithJson -eq $serviceJson) {
    Write-Host "OK: Odpowiedzi sa identyczne." -ForegroundColor Green
} else {
    Write-Host "ROZNICA: Odpowiedzi sie roznia!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Monolith:"
    Write-Host $monolithJson
    Write-Host "Service:"
    Write-Host $serviceJson
}
