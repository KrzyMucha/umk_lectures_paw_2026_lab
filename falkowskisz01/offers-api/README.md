# offers-api

Prosty CRUD API w Symfony 7 + PHP 8.3 + PostgreSQL 15.

## Wymagania

- Docker
- Docker Compose

## Uruchomienie

```bash
docker compose up -d --build
docker compose exec app composer install
docker compose exec app php bin/console doctrine:migrations:migrate --no-interaction
```

API będzie dostępne pod `http://localhost:8000`.

## Endpointy

- `GET /offers` – lista ofert
- `GET /offers/{id}` – szczegóły oferty
- `POST /offers` – utworzenie oferty
- `PUT /offers/{id}` – aktualizacja oferty
- `DELETE /offers/{id}` – usunięcie oferty

## Przykładowy payload (POST/PUT)

```json
{
  "title": "Laptop",
  "description": "Nowy laptop 15 cali",
  "price": 4999.99
}
```
