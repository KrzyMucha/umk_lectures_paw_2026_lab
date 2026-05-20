# 🚀 GCP Migration - QUICK START (May 2026)

**Projekt:** `paw-2026-496213` | **Region:** `europe-central2`

---

## ⚡ Szybko (5 minut)

### 1️⃣ Włącz IAM → Usuń HTTP 403

Konto `falkowskisz01@gmail.com` nie ma uprawnienia `run.services.setIamPolicy`. Użyj skryptu:

```bash
./scripts/setup-cloud-run-iam.sh
```

Lub ręcznie:

```bash
# mini-allegro
gcloud run services add-iam-policy-binding mini-allegro \
  --region=europe-central2 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=paw-2026-496213

# purchase-service-dev
gcloud run services add-iam-policy-binding purchase-service-dev \
  --region=europe-central2 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=paw-2026-496213
```

**Czekaj 30-60 sekund na propagację.**

### 2️⃣ Uruchom migracje (DEV)

```bash
./scripts/gcp-migration.sh migrate-db dev
```

### 3️⃣ Build & deploy product-review-service

```bash
./scripts/gcp-migration.sh deploy-product-review
```

### 4️⃣ Uruchom testy

```bash
./scripts/gcp-migration.sh run-tests
```

---

## 📋 Co się zmieniło?

| Plik | Co | Dlaczego |
|------|-----|---------|
| `infra/main.tf` | Odkomentowany IAM dla `mini-allegro` | Public access (403 → 200) |
| `infra/purchase-service.tf` | Odkomentowany IAM dla `purchase-service` | Public access (403 → 200) |
| `scripts/gcp-migration.sh` | Nowy skrypt | Automatyzacja migrate + deploy + test |
| `GCP_MIGRATION_STEPS.md` | Pełna instrukcja | Szczegółowe kroki |

---

## 🔄 Pełna Automatyzacja (One-Liner)

```bash
# Setup IAM ręcznie
./scripts/setup-cloud-run-iam.sh

# Czekaj 30-60 sekund, potem reszta automatyzacji
./scripts/gcp-migration.sh all
```

Robi:
1. ✅ Setup IAM (public access)
2. ✅ DB migracje (DEV)
3. ✅ Build + deploy product-review-service
4. ✅ Integration tests

---

## 🎯 Status Po Każdym Kroku

```bash
# Check IAM
gcloud run services get-iam-policy mini-allegro \
  --region=europe-central2 --project=paw-2026-496213

# Check HTTP access
curl -i https://mini-allegro-697507505034.europe-central2.run.app/health
# Powinno być: HTTP 200 (zamiast 403)

# Check DB migrations
gcloud sql connect mini-allegro-db-dev \
  --user=app --project=paw-2026-496213 \
  -- -c "SELECT COUNT(*) FROM doctrine_migration_versions;"

# Check product-review-service
curl -i https://product-review-service-dev-<ID>.europe-central2.run.app/health
```

---

## 🧪 Testy Integracyjne

```bash
# Setup
pip install -r integ-tests/requirements.txt

# Ustaw URLs
export MINI_ALLEGRO_URL="https://mini-allegro-697507505034.europe-central2.run.app"
export PURCHASE_SERVICE_URL="https://purchase-service-dev-697507505034.europe-central2.run.app"
export PRODUCT_REVIEW_SERVICE_URL="https://product-review-service-dev-<ID>.europe-central2.run.app"

# Run all
pytest integ-tests/ -v

# Or specific
pytest integ-tests/test_users.py -v
pytest integ-tests/test_products.py -v
pytest integ-tests/test_offers.py -v
pytest integ-tests/test_product_reviews.py -v
```

---

## 🚨 Troubleshooting

### ❌ HTTP 403 (Access Denied)

```bash
# Check IAM status
gcloud run services get-iam-policy mini-allegro \
  --region=europe-central2 --project=paw-2026-496213

# Manually add if missing
gcloud run services add-iam-policy-binding mini-allegro \
  --region=europe-central2 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=paw-2026-496213
```

### ❌ DB migrations failed

```bash
# Check Cloud SQL status
gcloud sql instances describe mini-allegro-db-dev \
  --project=paw-2026-496213

# Check logs
gcloud sql operations list --instance=mini-allegro-db-dev --project=paw-2026-496213

# Restart if needed
gcloud sql instances restart mini-allegro-db-dev --project=paw-2026-496213
```

### ❌ Docker image build failed

```bash
# Check Maven
cd services/product-review-service
mvn clean package -DskipTests

# Check Artifact Registry auth
gcloud auth configure-docker europe-central2-docker.pkg.dev
```

---

## 📚 Dokumentacja

- **Pełne kroki:** [GCP_MIGRATION_STEPS.md](./GCP_MIGRATION_STEPS.md)
- **Terraform:** [infra/main.tf](./infra/main.tf)
- **Migracje:** [services/symphony-monolith/migrations/](./services/symphony-monolith/migrations/)
- **Testy:** [integ-tests/](./integ-tests/)

---

## ✅ Checklist

- [ ] IAM ustawiony ręcznie (`gcloud run services add-iam-policy-binding`)
- [ ] HTTP 200 na mini-allegro (zamiast 403)
- [ ] HTTP 200 na purchase-service (zamiast 403)
- [ ] DB migracje uruchomione
- [ ] product-review-service deployed
- [ ] Testy integracyjne przechodzą

---

## 🔗 Live URLs

| Service | URL | Status |
|---------|-----|--------|
| **mini-allegro** | https://mini-allegro-697507505034.europe-central2.run.app | ✓ Public |
| **purchase-service** | https://purchase-service-dev-697507505034.europe-central2.run.app | ✓ Public |
| **product-review-service** | https://product-review-service-dev-<ID>.europe-central2.run.app | → Deploy |

---

**Gotowe do pracy? Zaczynaj od komendy `terraform apply` w `infra/`** 🚀

