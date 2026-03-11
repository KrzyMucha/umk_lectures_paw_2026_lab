# Mini Allegro - Infrastructure

## Wymagania

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/) z obsługą buildx

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

## Kolejność operacji

```
terraform apply (Artifact Registry) → docker push → terraform apply (Cloud Run)
```

> Artifact Registry musi istnieć przed pushem obrazu. Cloud Run musi być wdrożony po pushu obrazu.
