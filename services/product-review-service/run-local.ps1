$CONTAINER_NAME = "product-review-service"
$IMAGE_NAME = "product-review-service"

# Jesli zmienne nie sa ustawione w sesji, czytamy z .env.local w katalogu glownym projektu
$envFile = Join-Path $PSScriptRoot "../../.env.local"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^GOOGLE_APPLICATION_CREDENTIALS=(.+)$") {
            if (-not $env:GOOGLE_APPLICATION_CREDENTIALS) {
                $env:GOOGLE_APPLICATION_CREDENTIALS = $Matches[1]
                Write-Host "GOOGLE_APPLICATION_CREDENTIALS zaladowany z .env.local"
            }
        }
        if ($_ -match "^GOOGLE_CLOUD_PROJECT=(.+)$") {
            if (-not $env:GOOGLE_CLOUD_PROJECT) {
                $env:GOOGLE_CLOUD_PROJECT = $Matches[1]
                Write-Host "GOOGLE_CLOUD_PROJECT zaladowany z .env.local"
            }
        }
        if ($_ -match "^FIRESTORE_EMULATOR_HOST=(.+)$") {
            if (-not $env:FIRESTORE_EMULATOR_HOST) {
                $env:FIRESTORE_EMULATOR_HOST = $Matches[1]
            }
        }
    }
}

switch ($args[0]) {
    "stop" {
        Write-Host "Stopping $CONTAINER_NAME..."
        docker stop $CONTAINER_NAME 2>$null
        docker rm $CONTAINER_NAME 2>$null
        Write-Host "Stopped."
    }
    "logs" {
        docker logs -f $CONTAINER_NAME
    }
    default {
        Write-Host "Building $IMAGE_NAME..."
        docker build -t $IMAGE_NAME .

        docker stop $CONTAINER_NAME 2>$null
        docker rm $CONTAINER_NAME 2>$null

        Write-Host "Starting $CONTAINER_NAME..."
        $runArgs = @(
            "run", "-d",
            "--name", $CONTAINER_NAME,
            "-p", "8081:8080",
            "-e", "PORT=8080"
        )

        if ($env:GOOGLE_APPLICATION_CREDENTIALS) {
            # Montujemy plik credentials do kontenera (Docker nie ma dostepu do dysku Windows)
            $runArgs += "-v"
            $runArgs += "$($env:GOOGLE_APPLICATION_CREDENTIALS):/tmp/gcp-credentials.json:ro"
            $runArgs += "-e"
            $runArgs += "GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json"
        }

        if ($env:GOOGLE_CLOUD_PROJECT) {
            $runArgs += "-e"
            $runArgs += "GOOGLE_CLOUD_PROJECT=$env:GOOGLE_CLOUD_PROJECT"
        }

        if ($env:FIRESTORE_EMULATOR_HOST) {
            $runArgs += "-e"
            $runArgs += "FIRESTORE_EMULATOR_HOST=$env:FIRESTORE_EMULATOR_HOST"
        }

        $runArgs += $IMAGE_NAME
        docker @runArgs

        Write-Host "Service running at http://localhost:8081"
    }
}
