# Purchase Service (Flask)

Krok 1 wydzielenia serwisu `Purchase` z monolitu Symfony.

## Endpointy

- `GET /health`
- `GET /purchases` (hardkodowana lista)
- `GET /purchases/<id>` (hardkodowany rekord)

Format JSON na `/purchases` odpowiada formatowi z monolitu (`id`, `userId`, `offerId`, `quantity`, `pricePerUnit`, `totalPrice`, `status`).

## Uruchomienie lokalne

```bash
cd services/purchase-service
./run-local.sh
```

Serwis uruchomi się na `http://localhost:8081`.

## Sterowanie kontenerem

```bash
./run-local.sh stop
./run-local.sh logs
```

## Cloud Run

Dockerfile jest multi-stage i serwis nasłuchuje na porcie z `PORT` (domyślnie `8080`).
