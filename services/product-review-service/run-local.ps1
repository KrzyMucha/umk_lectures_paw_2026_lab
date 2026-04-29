$CONTAINER_NAME = "product-review-service"
$IMAGE_NAME = "product-review-service"

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

        if ($env:DATABASE_URL) {
            $runArgs += "-e"
            $runArgs += "DATABASE_URL=$env:DATABASE_URL"
        }

        $runArgs += $IMAGE_NAME
        docker @runArgs

        Write-Host "Service running at http://localhost:8081"
    }
}
