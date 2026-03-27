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
cd ../../infra
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
cd ../../infra
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

Testy API są w katalogu [integ-tests/test_api.py](../../integ-tests/test_api.py) i używają `pytest`.

### Uruchomienie lokalne

1. Uruchom aplikację (np. przez Docker Compose):

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.override.yaml up -d --build
```

2. Zainstaluj zależności testowe i uruchom testy:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Domyślnie testy strzelają pod `http://localhost:8080`. Możesz zmienić URL:

```bash
APP_BASE_URL=https://twoj-serwis.run.app pytest
```

### GitHub Actions + GCP (Cloud Run)

Workflow CI uruchamia:

- testy lokalne na `docker compose` (zawsze),
- testy pod wdrożony URL z GCP (opcjonalnie).

Aby uruchamiać testy pod Cloud Run w GitHub Actions, ustaw w repo:

- `Settings -> Secrets and variables -> Actions -> Variables`
- zmienną `GCP_APP_BASE_URL`, np. `https://mini-allegro-xxxxx-ew.a.run.app`

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

W repo jest gotowy skrypt: `scripts/deploy_prod_with_rollback.sh`.

Co robi:

-   zapamiętuje poprzednią rewizję Cloud Run,
-   deployuje nową rewizję,
-   wykonuje healthcheck,
-   przy błędzie wykonuje rollback ruchem 100% na poprzednią rewizję przez:
    `gcloud run services update-traffic`.

Użycie:

```bash
chmod +x scripts/deploy_prod_with_rollback.sh

./scripts/deploy_prod_with_rollback.sh \
  --service mini-allegro \
  --region europe-central2 \
  --project project-f5f4f6f0-acae-485b-a16 \
  --image europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest
```

Opcjonalnie możesz zmienić endpoint healthcheck i retry:

```bash
./scripts/deploy_prod_with_rollback.sh \
  --service mini-allegro \
  --region europe-central2 \
  --image europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest \
  --health-path /health \
  --retries 12 \
  --sleep-seconds 5
```
