#Requires -Version 5.1
<#
.SYNOPSIS
    Local development helper for symphony-monolith (Windows PowerShell version).

.EXAMPLE
    .\scripts\local-app.ps1 up
    .\scripts\local-app.ps1 stop
    .\scripts\local-app.ps1 logs
    .\scripts\local-app.ps1 test
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"

$ROOT_DIR   = (Resolve-Path "$PSScriptRoot\..").Path
$SERVICE_DIR = "$ROOT_DIR\services\symphony-monolith"
$DOCKER_DIR  = "$SERVICE_DIR\docker"
$COMPOSE_FILES = @("-f", "$DOCKER_DIR\docker-compose.yml", "-f", "$DOCKER_DIR\compose.override.yaml")

function Show-Usage {
    Write-Host @"
Usage:
  .\scripts\local-app.ps1 <command>

Commands:
  up         Build/start app; if already running, reuse and stream logs
  stop       Stop app container (without removing volumes)
  down       Stop stack and remove volumes
  restart    Recreate app container and stream logs (Ctrl+C stops app)
  logs       Show docker compose logs (follow mode)
  status     Show docker compose services status
  migrate    Run pending Doctrine migrations inside the container
  test       Run Python integration tests (integ-tests)
  help       Show this help

Examples:
  .\scripts\local-app.ps1 up
  .\scripts\local-app.ps1 stop
  .\scripts\local-app.ps1 logs
  .\scripts\local-app.ps1 test
"@
}

function Invoke-Compose {
    $dbUrl = if ($env:DATABASE_URL) { $env:DATABASE_URL } else { "postgresql://placeholder:placeholder@localhost:5432/placeholder" }
    $env:DATABASE_URL = $dbUrl
    docker compose @COMPOSE_FILES @args
}

function Test-AppRunning {
    $running = docker compose @COMPOSE_FILES ps --status running --services 2>$null
    return ($running -split "`n") -contains "app"
}

function Assert-Paths {
    if (-not (Test-Path $SERVICE_DIR -PathType Container)) {
        Write-Error "Service directory not found: $SERVICE_DIR"
        exit 1
    }
    if (-not (Test-Path "$DOCKER_DIR\docker-compose.yml" -PathType Leaf)) {
        Write-Error "docker-compose.yml not found in: $DOCKER_DIR"
        exit 1
    }
}

function Assert-PortFree {
    param([int]$Port = 8080)

    $used = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($used) {
        if (Test-AppRunning) {
            Write-Host "Port $Port is already in use, but compose service 'app' is running. Reusing existing app."
            Write-Host "Attaching logs (Ctrl+C detaches, app keeps running)..."
            Invoke-Compose logs -f app
            exit 0
        }

        Write-Error "Port $Port is already in use. Cannot start app."
        Write-Host ""
        Write-Host "Process using port ${Port}:"
        $used | ForEach-Object {
            $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
            Write-Host "  PID $($_.OwningProcess)  $($proc.Name)"
        }
        Write-Host ""
        $dockerOnPort = docker ps --filter "publish=$Port" --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}" 2>$null
        if ($dockerOnPort -and ($dockerOnPort -split "`n").Count -gt 1) {
            Write-Host "Docker containers publishing port ${Port}:"
            Write-Host $dockerOnPort
        }
        Write-Host "Free the port and try again (e.g. docker stop <id> or Stop-Process -Id <pid>)."
        exit 1
    }
}

$GCP_PROJECT       = "project-f5f4f6f0-acae-485b-a16"
$GCP_SQL_INSTANCE  = "mini-allegro-db-dev"
$DB_USER           = "app"
$DB_NAME           = "mini_allegro_dev"
$LOCAL_ENV_FILE    = "$ROOT_DIR\.env.local"

$TF_STATE_GCS = "gs://mini-allegro-tf-state/mini-allegro/dev/default.tfstate"
$LOCAL_ENV_FILE = "$ROOT_DIR\.env.local"

function Resolve-DevDatabaseUrl {
    if ($env:DATABASE_URL) { return }

    # 1. Try terraform (if installed)
    if (Get-Command terraform -ErrorAction SilentlyContinue) {
        $tfOutput = terraform -chdir="$ROOT_DIR\infra\dev" output -raw database_url 2>$null
        if ($tfOutput) {
            $env:DATABASE_URL = $tfOutput
            Write-Host "Using DATABASE_URL from terraform output: infra/dev.database_url"
            return
        }
    }

    # 2. Try cached .env.local
    if (Test-Path $LOCAL_ENV_FILE) {
        $cached = Get-Content $LOCAL_ENV_FILE | Where-Object { $_ -match "^DATABASE_URL=.+" }
        if ($cached) {
            $env:DATABASE_URL = ($cached -replace "^DATABASE_URL=", "").Trim()
            Write-Host "Using DATABASE_URL from .env.local" -ForegroundColor Green
            return
        }
    }

    # 3. Read DATABASE_URL directly from Terraform state in GCS
    if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Error "Nie znaleziono ani terraform, ani gcloud. Ustaw DATABASE_URL recznie."
        exit 1
    }

    Write-Host "Pobieram DATABASE_URL z Terraform state (GCS)..." -ForegroundColor Cyan

    $stateJson = gcloud storage cat $TF_STATE_GCS 2>$null
    if (-not $stateJson) {
        Write-Error "Nie udalo sie pobrac terraform state z GCS. Sprawdz czy jestes zalogowany: gcloud auth login"
        exit 1
    }

    $url = $stateJson | python -c "import sys,json; s=json.load(sys.stdin); print(s['outputs']['database_url']['value'])" 2>$null
    if (-not $url) {
        Write-Error "Nie udalo sie odczytac database_url z terraform state."
        exit 1
    }

    $env:DATABASE_URL = $url
    "DATABASE_URL=$url" | Out-File -FilePath $LOCAL_ENV_FILE -Encoding utf8
    Write-Host "DATABASE_URL pobrany z GCS i zapisany do .env.local" -ForegroundColor Green
}

function Find-Python {
    foreach ($cmd in @("python", "python3", "py")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) { return $cmd }
    }
    Write-Error "Python not found. Install Python 3 and make sure it is on your PATH."
    exit 1
}

# ── main ────────────────────────────────────────────────────────────────────

Assert-Paths

switch ($Command) {
    "up" {
        Assert-PortFree 8080
        Resolve-DevDatabaseUrl
        Invoke-Compose up --build --no-deps app
    }
    "stop" {
        Invoke-Compose stop app
    }
    "down" {
        Invoke-Compose down -v
    }
    "restart" {
        Invoke-Compose down -v
        Assert-PortFree 8080
        Resolve-DevDatabaseUrl
        Invoke-Compose up --build --no-deps app
    }
    "logs" {
        Invoke-Compose logs -f app
    }
    "status" {
        Invoke-Compose ps app
    }
    "migrate" {
        $containerId = docker compose @COMPOSE_FILES ps -q app 2>$null
        if (-not $containerId) {
            Write-Error "App container is not running. Start it first with: .\scripts\local-app.ps1 up"
            exit 1
        }
        docker exec $containerId php bin/console doctrine:migrations:migrate --no-interaction
    }
    "test" {
        $VENV_DIR = "$ROOT_DIR\.venv"
        $PY_REQ   = "$SERVICE_DIR\requirements-dev.txt"
        $python   = Find-Python

        if (-not (Test-Path $VENV_DIR -PathType Container)) {
            & $python -m venv $VENV_DIR
        }

        & "$VENV_DIR\Scripts\Activate.ps1"
        pip install -r $PY_REQ

        $baseUrl = if ($env:APP_BASE_URL) { $env:APP_BASE_URL } else { "http://localhost:8080" }
        $env:APP_BASE_URL = $baseUrl
        pytest "$ROOT_DIR\integ-tests"
    }
    { $_ -in @("help", "-h", "--help") } {
        Show-Usage
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Usage
        exit 1
    }
}
