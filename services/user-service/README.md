# User Service (FastAPI)

Serwis oparty o FastAPI, ktory czyta i zapisuje userow bezposrednio do bazy PostgreSQL (ta sama tabela `"user"`, ktorej uzywa Symfony):

- `GET /users` - lista userow
- `GET /user/{id}` - pojedynczy user po ID
- `GET /users-super` - userzy z przypietym `superSellerId`
- `POST /users` - tworzenie usera

Serwis zwraca shape zgodny z monolitem Symfony (`User::toArray()`), plus `superSellerId` dla endpointu `/users-super`:

- `id` (int)
- `email` (string)
- `firstName` (string)
- `lastName` (string)
- `fullName` (string)
- `roles` (array string)
- `isCustomer` (bool)
- `isSeller` (bool)

## Wymagane zmienne srodowiskowe

- `DATABASE_URL` - np. `postgresql://app:pass@host:5432/mini_allegro_dev?serverVersion=15&charset=utf8`

Parametry `serverVersion` i `charset` sa automatycznie ignorowane po stronie Pythona, wiec mozesz podac ten sam URL co do Symfony.

## Aktualny format odpowiedzi z monolitu (do wklejenia)

Monolit nie byl uruchomiony podczas przygotowywania tego serwisu.
Wklej tutaj wynik polecenia po uruchomieniu Symfony:

```bash
curl -s http://localhost:8080/users | python3 -m json.tool
```

## Uruchomienie lokalne (Docker)

```bash
cd services/user-service
docker build -t user-service:local .
docker run --rm -p 8080:8080 -e PORT=8080 -e DATABASE_URL="$DATABASE_URL" user-service:local
```

## Test endpointow

```bash
curl -s http://localhost:8080/users | python3 -m json.tool
curl -s http://localhost:8080/user/1 | python3 -m json.tool
curl -s http://localhost:8080/users-super | python3 -m json.tool
```

## Testy (pytest)

```bash
cd services/user-service
./.venv/bin/pip install -r requirements-dev.txt
./.venv/bin/pytest -q
```
