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
terraform apply
```

---

## 3. Build i push obrazu Docker

```bash
cd services/mini-allegro

docker buildx build --platform linux/amd64 --target prod \
  -t europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest \
  --push .
```

> Na Apple Silicon (ARM) flaga `--platform linux/amd64` jest wymagana.

---

## 4. Deploy Cloud Run

```bash
cd infra
terraform apply
```

---

## 5. Weryfikacja

```bash
curl $(terraform output -raw service_url)/offers
```

---

## Testy (Python, bez PHPUnit)

Testy API są w katalogu [services/mini-allegro/tests_python](services/mini-allegro/tests_python) i używają `pytest`.

### Uruchomienie lokalne

1. Uruchom aplikację (np. przez Docker Compose):

```bash
docker compose up -d --build
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
