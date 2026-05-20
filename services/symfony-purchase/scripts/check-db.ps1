param(
    [int]$Checks = 20,
    [int]$SleepMs = 300,
    [int]$TimeoutSeconds = 5
)

$ErrorActionPreference = 'Stop'

$env:DB_CHECK_COUNT = "$Checks"
$env:DB_CHECK_SLEEP_MS = "$SleepMs"
$env:DB_CONNECT_TIMEOUT_SECONDS = "$TimeoutSeconds"

php "$(Join-Path $PSScriptRoot 'test_db.php')"
exit $LASTEXITCODE
