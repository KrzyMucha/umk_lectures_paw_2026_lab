# Database connectivity check

Skrypt testuje połączenie do nowego serwisu bazodanowego wielokrotnie i zwraca błąd, jeżeli skuteczność testu jest mniejsza niż 100%.

## Wymagane zmienne środowiskowe

## Wymagane rozszerzenia PHP (CLI)

- Dla PostgreSQL: `pdo_pgsql`
- Dla MySQL: `pdo_mysql`

### Opcja 1: `DATABASE_URL`

Przykład PostgreSQL:

```bash
DATABASE_URL=postgresql://user:pass@127.0.0.1:5432/purchase_db
```

Przykład MySQL:

```bash
DATABASE_URL=mysql://user:pass@127.0.0.1:3306/purchase_db?charset=utf8mb4
```

### Opcja 2: osobne zmienne

- `DB_DRIVER` (`pgsql` lub `mysql`)
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_CHARSET` (opcjonalnie dla MySQL)

## Uruchomienie (PowerShell)

```powershell
cd symfony-purchase
$env:DATABASE_URL = "postgresql://user:pass@127.0.0.1:5432/purchase_db"
./scripts/check-db.ps1 -Checks 30 -SleepMs 200 -TimeoutSeconds 5
```

## Kody wyjścia

- `0` – 100% testów zakończonych sukcesem
- `1` – błąd konfiguracji lub brak połączenia
- `2` – połączenie działa, ale skuteczność < 100%
