#testing push 1
# Mini Allegro - Infrastructure

## Wymagania

-   [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
-   [gcloud CLI](https://cloud.google.com/sdk/docs/install)
-   [Docker](https://docs.docker.com/get-docker/) z obsługą buildx

---

## 1. Uwierzytelnienie

```bash
# Zaloguj się do GCP
gcloud auth login

# Ustaw projekt
gcloud config set project project-f5f4f6f0-acae-485b-a16

# Skonfiguruj Docker do pushowania do Artifact Registry
gcloud auth configure-docker europe-central2-docker.pkg.dev
```

---

## 2. Terraform - utwórz infrastrukturę

```bash
cd infra
terraform init
terraform apply -var="alert_email=twoj.email@domena.pl"
```

---

## 3. Build i push obrazu Docker

### Opcja A – Google Cloud Build (zalecane, najszybsze)

Build działa natywnie na `linux/amd64` w GCP, blisko Artifact Registry. Cache warstw jest przechowywany w rejestrze między buildami (`mode=max` cachuje wszystkie etapy, w tym `base` z rozszerzeniami PHP).

```bash
cd services/symphony-monolith

gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=project-f5f4f6f0-acae-485b-a16 \
  .
```

### Opcja B – lokalny docker buildx z cache w rejestrze

Używa tego samego cache z Artifact Registry co Cloud Build. Na Apple Silicon wymagana flaga `--platform linux/amd64`.

```bash
cd services/symphony-monolith

REGISTRY=europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro

docker buildx build --platform linux/amd64 --target prod \
  --cache-from type=registry,ref=${REGISTRY}:cache \
  --cache-to   type=registry,ref=${REGISTRY}:cache,mode=max \
  -t ${REGISTRY}:latest \
  --push .
```

---

## 4. Deploy Cloud Run

```bash
cd infra
terraform apply -var="alert_email=twoj.email@domena.pl"
```

---

## 5. Weryfikacja

```bash
# Offers
curl $(terraform output -raw service_url)/offers

# Users
curl $(terraform output -raw service_url)/users

# Purchases (all)
curl $(terraform output -raw service_url)/purchases

# Purchases by offer
curl $(terraform output -raw service_url)/purchases/offer/1

# Health check
curl $(terraform output -raw service_url)/health
```

### Log Explorer (Cloud Logging)

W Cloud Logging -> Log Explorer użyj filtra:

```text
resource.type="cloud_run_revision"
resource.labels.service_name="mini-allegro"
severity>=WARNING
```

To pokaże warningi i błędy aplikacji z Cloud Run.

### Testowanie Alert Policy (5+ błędów w 5 minut)

1. **Endpoint testowy** – aplikacja ma endpoint `/health/error` który logruje ERROR i zwraca 500:

```bash
curl $(terraform output -raw service_url)/health/error
```

2. **Wyzwolenie alertu** – aby wyzwolić alertę, wyślij 5+ błędów w ciągu 5 minut:

```bash
# Bash loop – wysyła 10 błędów ciągle
for i in {1..10}; do
  curl -s $(terraform output -raw service_url)/health/error
  sleep 5  # opóźnienie między każdym błędem
done
```

3. **Weryfikacja**:
    - W Cloud Logging -> Logs Explorer, przefiltruj po severity=ERROR, resource.labels.service_name="mini-allegro"
    - W Cloud Monitoring -> Alerting -> Policies, sprawdź status "mini-allegro Cloud Run error burst"
    - Email powinnien przyjść na adres podany w `alert_email` w ciągu ~1 minuty od przekroczenia progu

---

## Testy (Python, bez PHPUnit)

Testy API są rozdzielone per encja i używają `pytest`:

- `integ-tests/test_offers.py`
- `integ-tests/test_users.py`
- `integ-tests/test_products.py`

### Uruchomienie lokalne

Możesz użyć skrótu przez skrypt pomocniczy:

```bash
./scripts/local-app.sh up
./scripts/local-app.sh stop
./scripts/local-app.sh status
./scripts/local-app.sh logs
./scripts/local-app.sh test
./scripts/local-app.sh down
```

Jeśli `./scripts/local-app.sh up` wykryje, że port `8080` jest zajęty przez już działającą usługę `app` z Docker Compose, nie kończy się błędem — przełącza się w tryb „reuse” i tylko podpina logi.

1. Uruchom aplikację (np. przez Docker Compose):

```bash
terraform -chdir=infra/dev output -raw database_url
./scripts/local-app.sh up
```

`local-app.sh` automatycznie pobiera `DATABASE_URL` z `infra/dev` (`database_url`), więc lokalna instancja łączy się z bazą DEV w Cloud SQL.

2. Zainstaluj zależności testowe i uruchom testy:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/symphony-monolith/requirements-dev.txt
pytest integ-tests/test_offers.py
pytest integ-tests/test_users.py
pytest integ-tests/test_products.py
```

Domyślnie testy strzelają pod `http://localhost:8080`. Możesz zmienić URL:

```bash
APP_BASE_URL=https://twoj-serwis.run.app pytest integ-tests
```

### GitHub Actions + GCP (Cloud Run)

Workflowy deploy uruchamiają testy integracyjne oddzielnie dla `offers`, `users` i `products`, dzięki czemu od razu widać, która encja failuje.

Wymagane sekrety GitHub Actions:

- `DEV_DATABASE_URL`
- `PROD_DATABASE_URL`
- `TF_STATE_BUCKET` (nazwa bucketu GCS na terraform state, np. `mini-allegro-tf-state`)

Wartości możesz pobrać z Terraform:

```bash
terraform -chdir=infra/dev output -raw database_url
terraform -chdir=infra/prod output -raw database_url
```

---

## Kolejność operacji

```
terraform apply (Artifact Registry) → docker push → terraform apply (Cloud Run)
```

> Artifact Registry musi istnieć przed pushem obrazu. Cloud Run musi być wdrożony po pushu obrazu.

```shell
gcloud run deploy mini-allegro \
    --image europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest \
    --region europe-central2
```

## Deploy PROD z automatycznym rollbackiem

W repo jest gotowy skrypt: `services/symphony-monolith/scripts/deploy_prod_with_rollback.sh`.

Co robi:

-   zapamiętuje poprzednią rewizję Cloud Run,
-   deployuje nową rewizję,
-   wykonuje healthcheck,
-   przy błędzie wykonuje rollback ruchem 100% na poprzednią rewizję przez:
    `gcloud run services update-traffic`.

Użycie:

```bash
chmod +x services/symphony-monolith/scripts/deploy_prod_with_rollback.sh

./services/symphony-monolith/scripts/deploy_prod_with_rollback.sh \
  --service mini-allegro \
  --region europe-central2 \
  --project project-f5f4f6f0-acae-485b-a16 \
  --image europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest
```

Opcjonalnie możesz zmienić endpoint healthcheck i retry:

```bash
./services/symphony-monolith/scripts/deploy_prod_with_rollback.sh \
  --service mini-allegro \
  --region europe-central2 \
  --image europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest \
  --health-path /health \
  --retries 12 \
  --sleep-seconds 5
```
