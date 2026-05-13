# purchase-service (Flask)

Minimalny serwis Flask z hardkodowanymi danymi dla encji Purchase.

## Endpointy

- `GET /purchases` — lista zakupow
- `GET /purchases/{id}` — pojedynczy zakup

## Uruchomienie lokalne (Docker)

```bash
cd services/purchase-service
chmod +x run-local.sh
./run-local.sh
```

Serwis wystartuje pod: `http://localhost:8081`

## Zatrzymanie

```bash
./run-local.sh stop
```

## Logi

```bash
./run-local.sh logs
```
