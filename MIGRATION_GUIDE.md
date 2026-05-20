# Przewodnik migracji: GCP Project Migration

**Data migracji:** 2026-05-13  
**Stary projekt:** `project-f5f4f6f0-acae-485b-a16`  
**Nowy projekt:** `paw-2026-496213`  
**Region:** `europe-central2` (bez zmian)  
**Dane:** Start od nowa (bez backup'u)

---

## ✅ Co zostało zrobione automatycznie

- [x] Aktualizacja wszystkich `variables.tf` (6 plików) z nowym project ID
- [x] Aktualizacja `README.md` ze wszystkimi przykładami komendy
- [x] Aktualizacja `scripts/quick-dev-loop.sh`
- [x] Aktualizacja `services/symphony-monolith/scripts/deploy_prod_with_rollback.sh`

---

## 📋 Kroki do wykonania ręcznie

### 1️⃣ Zalogowanie do nowego projektu GCP

```bash
# Zaloguj się do GCP
gcloud auth login

# Ustaw nowy projekt jako domyślny
gcloud config set project paw-2026-496213

# Zweryfikuj
gcloud config get-value project
# Output: paw-2026-496213
```

### 2️⃣ Przygotowanie nowego projektu GCP

Upewnij się, że nowy projekt ma włączone niezbędne API:

```bash
# Włącz wymagane API
gcloud services enable \
  cloudrun.googleapis.com \
  cloudsql.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

### 3️⃣ Inicjalizacja Terraform (nowy state)

> ⚠️ **Ważne:** Terraform tworzy nowy state od zera. Stary project może zostać wyczyszczony później.

```bash
cd infra

# Usuń stary state (jeśli istnieje)
rm -rf .terraform
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*

# Zainicjalizuj dla nowego projektu
terraform init

# Weryfikacja
terraform validate
```

### 4️⃣ Wdrożenie infrastruktury (dev + prod)

```bash
cd infra

# Najpierw stwórz infrastrukturę (bez wdrażania aplikacji)
terraform apply \
  -var="alert_email=twoj.email@domena.pl" \
  -auto-approve
```

**Co zostanie utworzone:**

- Cloud SQL instancje: `mini-allegro-db-dev` i `mini-allegro-db-prod`
- Cloud SQL bazy: `mini_allegro_dev` i `mini_allegro_prod`
- Artifact Registry repository: `mini-allegro`
- Cloud Monitoring Alert Policy: `mini-allegro Cloud Run error burst`

### 5️⃣ Konfiguracja Docker dla Artifact Registry

```bash
# Autoryzuj Docker do pushowania do nowego rejestru
gcloud auth configure-docker europe-central2-docker.pkg.dev

# Zweryfikuj
gcloud auth list
```

### 6️⃣ Build i Push obrazu Docker

#### Opcja A: Google Cloud Build (zalecane)

```bash
cd services/symphony-monolith

gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=paw-2026-496213 \
  .

# Obserwuj build w Cloud Console:
# https://console.cloud.google.com/cloud-build/builds?project=paw-2026-496213
```

#### Opcja B: Lokalny docker buildx

```bash
cd services/symphony-monolith

REGISTRY=europe-central2-docker.pkg.dev/paw-2026-496213/mini-allegro/mini-allegro

docker buildx build --platform linux/amd64 --target prod \
  --cache-from type=registry,ref=${REGISTRY}:cache \
  --cache-to   type=registry,ref=${REGISTRY}:cache,mode=max \
  -t ${REGISTRY}:latest \
  --push .
```

### 7️⃣ Deploy aplikacji na Cloud Run

```bash
# Wdróż Cloud Run dla aplikacji głównej
cd infra
terraform apply \
  -var="alert_email=twoj.email@domena.pl" \
  -auto-approve

# Weryfikuj deployment
terraform output
```

### 8️⃣ Weryfikacja (Health Check)

```bash
# Pobierz URL usługi
SERVICE_URL=$(cd infra && terraform output -raw service_url)

# Sprawdź health
curl "$SERVICE_URL/health"

# Sprawdź dostępne endpoints
curl "$SERVICE_URL/offers"
curl "$SERVICE_URL/users"
curl "$SERVICE_URL/purchases"
```

---

## 🧪 Testy integracyjne

```bash
# Zainstaluj zależności
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/symphony-monolith/requirements-dev.txt

# Uruchom testy (trafią do aplikacji w Cloud Run)
APP_BASE_URL=$(cd infra && terraform output -raw service_url) \
  pytest integ-tests/test_offers.py -v

# Lub wszystkie testy
pytest integ-tests/ -v
```

---

## 🔄 Migracja danych (jeśli potrzebna)

Aktualne podejście: **Start od nowa** (bez danych)

Jeśli jednak chciałbyś przenieść dane ze starego projektu:

```bash
# 1. Zrób dump z Database DEV (stary projekt)
gcloud sql export sql \
  --project=paw-2026-496213 \
  mini-allegro-db-dev \
  gs://bucket-name/dump-dev.sql

# 2. Zaimportuj do nowego projektu
gcloud sql import sql \
  --project=paw-2026-496213 \
  mini-allegro-db-dev \
  gs://bucket-name/dump-dev.sql
```

---

## 🧹 Cleanup (po weryfikacji)

Po potwierdzeniu, że wszystko działa na nowym projekcie, możesz wyczyścić stary:

```bash
# ⚠️ OSTRZEŻENIE: To usunie wszystkie zasoby!

# Usuń infrastrukturę ze starego projektu
gcloud config set project project-f5f4f6f0-acae-485b-a16
cd infra
terraform destroy -auto-approve

# Usuń sam projekt (opcjonalnie)
gcloud projects delete project-f5f4f6f0-acae-485b-a16
```

---

## 📊 Monitoring migracji

**Cloud Console:** https://console.cloud.google.com/welcome?project=paw-2026-496213

Przydatne linki:

- [Cloud Run Services](https://console.cloud.google.com/run?project=paw-2026-496213)
- [Cloud SQL Instancje](https://console.cloud.google.com/sql/instances?project=paw-2026-496213)
- [Artifact Registry](https://console.cloud.google.com/artifacts/docker/paw-2026-496213/europe-central2?project=paw-2026-496213)
- [Cloud Build History](https://console.cloud.google.com/cloud-build/builds?project=paw-2026-496213)
- [Cloud Logs](https://console.cloud.google.com/logs/query?project=paw-2026-496213)

---

## 🆘 Rozwiązywanie problemów

### Problem: `terraform init` failuje z błędem GCP

**Rozwiązanie:** Sprawdź, czy jesteś zalogowany:

```bash
gcloud auth list
gcloud config list
```

### Problem: Docker push failuje

**Rozwiązanie:** Ponownie skonfiguruj Docker:

```bash
gcloud auth configure-docker europe-central2-docker.pkg.dev
```

### Problem: Cloud Run deployment failuje

**Rozwiązanie:** Sprawdź logi:

```bash
gcloud run services describe mini-allegro --region=europe-central2
gcloud run services logs read mini-allegro --region=europe-central2 --limit=50
```

### Problem: Database connection timeout

**Rozwiązanie:** Sprawdź autorizowane sieci w Cloud SQL:

```bash
gcloud sql instances describe mini-allegro-db-dev
```

---

## ✨ Następne kroki

1. **GitHub Actions secrets** – Zaktualizuj `DEV_DATABASE_URL` i `PROD_DATABASE_URL` w GitHub Secrets
2. **Domain/DNS** – Jeśli używasz domeny, zmień rekordy DNS na nowy service URL
3. **Documentation** – Zaktualizuj dokumentację zespołu z nowym URL'em
4. **Backup strategy** – Skonfiguruj automatyczne backupy Cloud SQL

---

Migracja zakończona! 🎉
