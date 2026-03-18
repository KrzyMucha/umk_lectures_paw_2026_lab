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
