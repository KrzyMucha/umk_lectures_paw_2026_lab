# Jesli DATABASE_URL nie jest ustawiony w srodowisku, czytamy z .env.local w katalogu glownym projektu
if (-not $env:DATABASE_URL) {
    $envFile = Join-Path $PSScriptRoot "../../.env.local"
    if (Test-Path $envFile) {
        $line = Get-Content $envFile | Where-Object { $_ -match "^DATABASE_URL=" } | Select-Object -First 1
        if ($line) {
            $env:DATABASE_URL = $line.Substring("DATABASE_URL=".Length)
            Write-Host "DATABASE_URL zaladowany z .env.local"
        }
    }
}

if (-not $env:DATABASE_URL) {
    Write-Host "BLAD: DATABASE_URL nie jest ustawiony i nie znaleziono .env.local" -ForegroundColor Red
    exit 1
}

docker compose -f docker/docker-compose.yml up
