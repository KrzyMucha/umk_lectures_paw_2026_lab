# Jak odpalić testy integracyjne lokalnie (Windows)

Testy dla `/reviews-super` znajdują się w `integ-tests/test_super_reviews.py`.

---

## Wymagania

- Docker Desktop uruchomiony
- PowerShell

---

## Krok 1 — Ustaw lokalną bazę danych

Domyślnie aplikacja łączy się z Cloud SQL (zdalna baza dev). Żeby uniknąć problemów z migracjami,
użyj lokalnego PostgreSQL w Dockerze.

```powershell
$env:DATABASE_URL = "postgresql://app:app@db:5432/app"
docker compose -f services\symphony-monolith\docker\docker-compose.yml -f services\symphony-monolith\docker\compose.override.yaml up -d db
```

---

## Krok 2 — Uruchom aplikację

W tym samym terminalu (DATABASE_URL musi być ustawiony):

```powershell
.\scripts\local-app.ps1 up
```

Poczekaj aż zobaczysz:
```
[OK] Successfully migrated to version: ...
[...] PHP Development Server (...) started
```

---

## Krok 3 — Odpal testy (nowy terminal)

Tylko testy super-reviews:
```powershell
$env:APP_BASE_URL="http://localhost:8080"; .venv\Scripts\pytest integ-tests\test_super_reviews.py -v
```

Wszystkie testy integracyjne:
```powershell
.\scripts\local-app.ps1 test
```

---

## Zatrzymanie środowiska

```powershell
.\scripts\local-app.ps1 down
```
