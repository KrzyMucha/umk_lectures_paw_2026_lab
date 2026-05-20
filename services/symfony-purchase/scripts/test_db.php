#!/usr/bin/env php
<?php

declare(strict_types=1);

function envValue(string $key, ?string $default = null): ?string
{
    $value = getenv($key);
    if ($value === false || $value === '') {
        return $default;
    }

    return $value;
}

function parseDbUrl(string $databaseUrl): array
{
    $parts = parse_url($databaseUrl);
    if ($parts === false) {
        throw new RuntimeException('Invalid DATABASE_URL format.');
    }

    $scheme = $parts['scheme'] ?? null;
    if ($scheme === null) {
        throw new RuntimeException('DATABASE_URL is missing scheme.');
    }

    $map = [
        'postgres' => 'pgsql',
        'postgresql' => 'pgsql',
        'pgsql' => 'pgsql',
        'mysql' => 'mysql',
        'mariadb' => 'mysql',
    ];

    $driver = $map[strtolower($scheme)] ?? strtolower($scheme);
    $host = $parts['host'] ?? '127.0.0.1';
    $port = isset($parts['port']) ? (int) $parts['port'] : null;
    $user = $parts['user'] ?? null;
    $pass = $parts['pass'] ?? null;
    $dbName = isset($parts['path']) ? ltrim($parts['path'], '/') : '';

    parse_str($parts['query'] ?? '', $query);

    return [
        'driver' => $driver,
        'host' => $host,
        'port' => $port,
        'dbname' => $dbName,
        'user' => $user,
        'password' => $pass,
        'charset' => $query['charset'] ?? null,
    ];
}

function buildDsn(array $config): string
{
    $driver = $config['driver'];
    $host = $config['host'] ?? '127.0.0.1';
    $port = $config['port'] ?? null;
    $dbName = $config['dbname'] ?? '';
    $charset = $config['charset'] ?? null;

    if (!in_array($driver, ['pgsql', 'mysql'], true)) {
        throw new RuntimeException('Unsupported driver: ' . $driver . '. Supported: pgsql, mysql');
    }

    $dsn = sprintf('%s:host=%s', $driver, $host);
    if (!empty($port)) {
        $dsn .= ';port=' . $port;
    }
    if ($dbName !== '') {
        $dsn .= ';dbname=' . $dbName;
    }
    if ($driver === 'mysql' && !empty($charset)) {
        $dsn .= ';charset=' . $charset;
    }

    return $dsn;
}

function validatePdoExtension(string $driver): void
{
    $requiredExtension = match ($driver) {
        'pgsql' => 'pdo_pgsql',
        'mysql' => 'pdo_mysql',
        default => throw new RuntimeException('Unsupported driver: ' . $driver),
    };

    if (!extension_loaded($requiredExtension)) {
        throw new RuntimeException(
            sprintf('Missing PHP extension "%s" for driver "%s".', $requiredExtension, $driver)
        );
    }
}

function queryNowUtc(PDO $pdo, string $driver): ?string
{
    if ($driver === 'pgsql') {
        $stmt = $pdo->query('SELECT NOW()::text AS now_utc');
    } elseif ($driver === 'mysql') {
        $stmt = $pdo->query("SELECT UTC_TIMESTAMP() AS now_utc");
    } else {
        return null;
    }

    $row = $stmt?->fetch(PDO::FETCH_ASSOC);
    return $row['now_utc'] ?? null;
}

function runCheck(PDO $pdo, string $driver): array
{
    $start = microtime(true);

    $stmt = $pdo->query('SELECT 1 AS ok');
    $row = $stmt?->fetch(PDO::FETCH_ASSOC);

    if (($row['ok'] ?? null) != 1) {
        throw new RuntimeException('Health query returned unexpected value.');
    }

    $serverTime = queryNowUtc($pdo, $driver);

    $durationMs = (microtime(true) - $start) * 1000;

    return [
        'duration_ms' => round($durationMs, 2),
        'server_time_utc' => $serverTime,
    ];
}

try {
    $checks = (int) envValue('DB_CHECK_COUNT', '10');
    $sleepMs = (int) envValue('DB_CHECK_SLEEP_MS', '300');
    $timeoutSeconds = (int) envValue('DB_CONNECT_TIMEOUT_SECONDS', '5');

    if ($checks < 1) {
        throw new RuntimeException('DB_CHECK_COUNT must be >= 1.');
    }

    $config = [];
    $databaseUrl = envValue('DATABASE_URL');

    if ($databaseUrl !== null) {
        $config = parseDbUrl($databaseUrl);
    } else {
        $config = [
            'driver' => envValue('DB_DRIVER', 'pgsql'),
            'host' => envValue('DB_HOST', '127.0.0.1'),
            'port' => (int) envValue('DB_PORT', '5432'),
            'dbname' => envValue('DB_NAME', ''),
            'user' => envValue('DB_USER', ''),
            'password' => envValue('DB_PASSWORD', ''),
            'charset' => envValue('DB_CHARSET', null),
        ];
    }

    $dsn = buildDsn($config);
    validatePdoExtension($config['driver']);

    $pdoOptions = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_TIMEOUT => $timeoutSeconds,
    ];

    $pdo = new PDO($dsn, $config['user'] ?? null, $config['password'] ?? null, $pdoOptions);

    echo "DB connectivity test started\n";
    echo "Driver: {$config['driver']}\n";
    echo "Host: {$config['host']}\n";
    echo "Checks: {$checks}\n\n";

    $success = 0;
    $fail = 0;
    $durations = [];

    for ($index = 1; $index <= $checks; $index++) {
        try {
            $result = runCheck($pdo, $config['driver']);
            $success++;
            $durations[] = $result['duration_ms'];

            $timeSuffix = $result['server_time_utc'] !== null ? ' | server_time=' . $result['server_time_utc'] : '';
            echo sprintf("[%d/%d] OK  %.2f ms%s\n", $index, $checks, $result['duration_ms'], $timeSuffix);
        } catch (Throwable $checkError) {
            $fail++;
            echo sprintf("[%d/%d] FAIL %s\n", $index, $checks, $checkError->getMessage());
        }

        if ($index < $checks && $sleepMs > 0) {
            usleep($sleepMs * 1000);
        }
    }

    $successRate = round(($success / $checks) * 100, 2);
    $avgMs = count($durations) > 0 ? round(array_sum($durations) / count($durations), 2) : null;

    echo "\nSummary\n";
    echo "Success: {$success}\n";
    echo "Fail: {$fail}\n";
    echo "Success rate: {$successRate}%\n";
    echo 'Avg response: ' . ($avgMs !== null ? $avgMs . ' ms' : 'n/a') . "\n";

    if ($successRate < 100.0) {
        fwrite(STDERR, "\nConnectivity is below 100%.\n");
        exit(2);
    }

    echo "\nConnectivity looks stable at 100% for this test run.\n";
    exit(0);
} catch (Throwable $error) {
    fwrite(STDERR, 'DB connectivity test failed: ' . $error->getMessage() . PHP_EOL);
    exit(1);
}
