# GCP Migration - Gotowe Kroki (May 2026)

**Projekt:** `paw-2026-496213` | **Region:** `europe-central2`

---

## ✅ 1. Włączenie Public Access (IAM) - gcloud CLI

### ⚠️ Wiadomość Ważna

Konto `falkowskisz01@gmail.com` nie ma uprawnienia `run.services.setIamPolicy`. Terraform nie może automatycznie zastosować IAM.

### Rozwiązanie: Ręczne Zastosowanie przez gcloud

```bash
PROJECT=paw-2026-496213
REGION=europe-central2

# mini-allegro
gcloud run services add-iam-policy-binding mini-allegro \
  --region=$REGION \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=$PROJECT

# purchase-service-dev
gcloud run services add-iam-policy-binding purchase-service-dev \
  --region=$REGION \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=$PROJECT
```

**Output powinien zawierać:**
```yaml
bindings:
- members:
  - allUsers
  role: roles/run.invoker
```

**Czekaj 30-60 sekund na propagację.**

---

## 2️⃣ Migracje Bazy Danych - mini-allegro

### 2.1 Uruchomienie migracji Doctrine (DEV)

```bash
# Locals w mini-allegro:
PROJECT=paw-2026-496213
REGION=europe-central2
INSTANCE=mini-allegro-db-dev
DB_NAME=mini_allegro_dev
DB_USER=app

# Pobranie hasła z Terraform state lub Secret Manager
DB_PASSWORD=$(terraform -chdir=./infra output -json | jq -r '.dev_db_password.value' 2>/dev/null || echo "CHECK TERRAFORM STATE")

# Pobranie IP Cloud SQL
DB_IP=$(gcloud sql instances describe $INSTANCE --project=$PROJECT --format='value(ipAddresses[0].ipAddress)')

# Uruchomienie migracji w kontenerze mini-allegro
docker run --rm \
  -e DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_IP}:5432/${DB_NAME}?sslmode=require" \
  -e APP_ENV=prod \
  "${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/mini-allegro:latest" \
  php bin/console doctrine:migrations:migrate --no-interaction
```

**Alternatywnie (jeśli docker jest w Cloud Run):**
```bash
gcloud run jobs create migrate-mini-allegro \
  --image="${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/mini-allegro:latest" \
  --region=$REGION \
  --set-env-vars="DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_IP}:5432/${DB_NAME}?sslmode=require,APP_ENV=prod" \
  --execute \
  --wait \
  -- php bin/console doctrine:migrations:migrate --no-interaction
```

### 2.2 Sprawdzenie statusu migracji

```bash
gcloud sql connect $INSTANCE \
  --user=$DB_USER \
  --project=$PROJECT \
  --database=$DB_NAME \
  -- -c "SELECT version, executed_at FROM doctrine_migration_versions ORDER BY version DESC LIMIT 5;"
```

---

## 3️⃣ product-review-service - Build & Deploy

### 3.1 Build obrazu Docker

```bash
PROJECT=paw-2026-496213
REGION=europe-central2
SERVICE_NAME=product-review-service-dev

cd services/product-review-service

# Zaloguj się do Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build obrazu
docker build -t "${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/${SERVICE_NAME}:latest" .

# Push do Artifact Registry
docker push "${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/${SERVICE_NAME}:latest"
```

### 3.2 Deploy na Cloud Run

```bash
PROJECT=paw-2026-496213
REGION=europe-central2
SERVICE_NAME=product-review-service-dev

gcloud run deploy $SERVICE_NAME \
  --image="${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/${SERVICE_NAME}:latest" \
  --region=$REGION \
  --project=$PROJECT \
  --memory=512Mi \
  --cpu=1 \
  --port=8080 \
  --allow-unauthenticated \
  --no-traffic
```

**Wyniku:**
```
Service [product-review-service-dev] status: ✓ Ready at https://product-review-service-dev-<ID>.europe-central2.run.app
```

### 3.3 Dodanie URL w mini-allegro

Edytuj `infra/main.tf` - odkomentuj:
```hcl
env {
  name  = "PRODUCT_REVIEW_SERVICE_URL"
  value = "https://product-review-service-dev-<ID>.europe-central2.run.app"
}
```

Lub użyj data source:
```hcl
data "google_cloud_run_v2_service" "product_review_service" {
  name     = "product-review-service-dev"
  location = var.region
}

# W kontenerze mini-allegro:
env {
  name  = "PRODUCT_REVIEW_SERVICE_URL"
  value = data.google_cloud_run_v2_service.product_review_service.uri
}
```

Potem: `terraform apply`

---

## 4️⃣ Testy Integracyjne

```bash
# Zainstaluj zależności
pip install -r integ-tests/requirements.txt -q

# Ustaw zmienne środowiska
export MINI_ALLEGRO_URL="https://mini-allegro-697507505034.europe-central2.run.app"
export PURCHASE_SERVICE_URL="https://purchase-service-dev-697507505034.europe-central2.run.app"
export PRODUCT_REVIEW_SERVICE_URL="https://product-review-service-dev-<ID>.europe-central2.run.app"

# Uruchom testy
pytest integ-tests/ -v

# Lub poszczególne
pytest integ-tests/test_users.py -v
pytest integ-tests/test_products.py -v
pytest integ-tests/test_offers.py -v
pytest integ-tests/test_product_reviews.py -v
pytest integ-tests/test_super_reviews.py -v
pytest integ-tests/test_super_sellers.py -v
```

---

## 5️⃣ (Opcjonalnie) PROD Setup

### 5.1 Utwórz branch/varsów dla PROD

```bash
# Skopiuj i dostosuj
cp -r infra/dev infra/prod-new

# W infra/prod-new/variables.tf zmień:
# - db_instance_name = "mini-allegro-db-prod"
# - db_name = "mini_allegro_prod"
```

### 5.2 Deploy PROD

```bash
cd infra/prod-new
terraform init -backend-config="bucket=<YOUR_GCS_BUCKET>" -backend-config="prefix=prod"
terraform apply
```

---

## 🔗 Aktualne URL-e

| Serwis | URL |
|--------|-----|
| **mini-allegro (DEV)** | `https://mini-allegro-697507505034.europe-central2.run.app` |
| **purchase-service (DEV)** | `https://purchase-service-dev-697507505034.europe-central2.run.app` |
| **product-review-service (DEV)** | `https://product-review-service-dev-<ID>.europe-central2.run.app` |

---

## 📋 Checklist

- [ ] IAM ustawiony ręcznie (`gcloud run services add-iam-policy-binding`)
- [ ] Sprawdzenie dostępu HTTP 200 (zamiast 403)
- [ ] Migracje Doctrine uruchomione dla mini-allegro
- [ ] product-review-service image zbudowany i deployowany
- [ ] PRODUCT_REVIEW_SERVICE_URL dodana w mini-allegro env
- [ ] Testy integracyjne przechodzą
- [ ] (Opcjonalnie) PROD setup

---

## 🆘 Troubleshooting

### ❌ Terraform apply fail: Permission 'run.services.setIamPolicy' denied

**Przyczyna:** Konto `falkowskisz01@gmail.com` nie ma uprawnienia do ustawiania IAM na Cloud Run.

**Rozwiązanie:** Użyj `gcloud CLI` zamiast Terraform:

```bash
gcloud run services add-iam-policy-binding mini-allegro \
  --region=europe-central2 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=paw-2026-496213

gcloud run services add-iam-policy-binding purchase-service-dev \
  --region=europe-central2 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=paw-2026-496213
```

### ❌ HTTP 403 po ustawieniu IAM
```bash
# Sprawdzenie IAM
gcloud run services get-iam-policy mini-allegro --region=europe-central2 --project=paw-2026-496213

# Powinna być linia:
# - allUsers -> roles/run.invoker

# Jeśli nie, dodaj ręcznie:
gcloud run services add-iam-policy-binding mini-allegro \
  --region=europe-central2 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=paw-2026-496213
```

### Migracje się zawieszają
```bash
# Sprawdzenie Cloud SQL connectivity
gcloud sql instances describe mini-allegro-db-dev --project=paw-2026-496213 --format='value(state,ipAddresses)'

# Restart instancji
gcloud sql instances restart mini-allegro-db-dev --project=paw-2026-496213
```

### product-review-service nie buduje się
```bash
# Sprawdzenie Maven build
cd services/product-review-service
mvn clean package -DskipTests

# Jeśli są problemy z zależnościami:
mvn dependency:tree
```

---

## 📝 Notatki

- **State:** Terraform state w `infra/terraform.tfstate` i `infra/terraform.tfstate.backup`
- **Images:** Wszystkie obrazy w `${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/`
- **Migracje:** Doctrine migrations są w `services/symphony-monolith/migrations/`
- **Baza:** PostgreSQL 15, auth via Cloud SQL Proxy lub IP allowlist

