# Purchase Service (Flask)

Krok 1-4 wydzielenia serwisu `Purchase` z monolitu Symfony.

## Endpointy

- `GET /health` — Health check endpoint
- `GET /purchases` — Lista wszystkich zakupów (z bazy lub hardkodowana)
- `GET /purchases/<id>` — Pojedynczy zakup po ID (z bazy lub hardkodowany)

Format JSON na `/purchases` odpowiada formatowi z monolitu: `id`, `userId`, `offerId`, `quantity`, `pricePerUnit`, `totalPrice`, `status`.

## Uruchomienie lokalne

### Bez bazy danych (hardkodowane dane)

```bash
cd services/purchase-service
./run-local.sh
```

Serwis uruchomi się na `http://localhost:8081` i zwróci hardkodowane dane.

### Z bazą danych (PostgreSQL)

Upewnij się, że Cloud SQL Proxy jest uruchomiony:

```bash
cloud-sql-proxy PROJECT_ID:europe-central2:INSTANCE_NAME --port=5433
```

Następnie uruchom serwis z `DATABASE_URL`:

```bash
cd services/purchase-service
DATABASE_URL="postgresql://app:app@host.docker.internal:5433/app" ./run-local.sh
```

Lub w docker-compose (z repozytorium):

```bash
cd services/symphony-monolith/docker
docker-compose up
```

## Sterowanie kontenerem

```bash
./run-local.sh stop      # Zatrzymaj kontener
./run-local.sh logs      # Pokaż logi
```

## Cloud Run

- Dockerfile: multi-stage build
- Serwis nasłuchuje na porcie `PORT` (domyślnie `8080`)
- W produkcji: łączy się do Cloud SQL przez Proxy
- Zmienne środowiskowe: `PORT`, `DATABASE_URL` (jeśli ustawiona)
- Publicznie dostępny: `roles/run.invoker` dla `allUsers`

## Database

### Schemat tabeli

Tabela `purchase` w PostgreSQL:

```sql
CREATE TABLE purchase (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    offer_id INT NOT NULL,
    quantity INT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    status VARCHAR(32) NOT NULL
);
```

### Fallback

Jeśli `DATABASE_URL` nie jest ustawiona lub połączenie do bazy się nie uda, serwis automatycznie wraca do hardkodowanych danych.

## Integracja z monolitem

PurchaseController w monolicie deleguje GET /purchases do tego serwisu:

- Monolith: `GET /purchases` → `PURCHASE_SERVICE_URL/purchases`
- Bezpośrednio: `GET http://localhost:8081/purchases`

Konfiguracja zmiennej `PURCHASE_SERVICE_URL`:

- Lokalnie w `.env`: `PURCHASE_SERVICE_URL=http://host.docker.internal:8081`
- Cloud Run: Terraform ustawia na `google_cloud_run_v2_service.purchase_service.uri`
