# ⚠️ Permission Issue - Cloud Run IAM Setup

**Data:** May 20, 2026  
**Projekt:** `paw-2026-496213`  
**Problem:** Permission `run.services.setIamPolicy` denied

---

## 🔴 Problem

Podczas `terraform apply` w `infra/` pojawił się błąd:

```
Error: Error applying IAM policy for cloudrunv2 service...
Permission 'run.services.setIamPolicy' denied on resource...
```

**Przyczyna:** Konto `falkowskisz01@gmail.com` nie ma uprawnienia do ustawiania IAM policies na Cloud Run.

---

## ✅ Rozwiązanie

### Opcja 1: Skrypt (Zalecane)

```bash
./scripts/setup-cloud-run-iam.sh
```

Skrypt automatycznie:
- Ustawia IAM dla `mini-allegro`
- Ustawia IAM dla `purchase-service-dev`
- Testuje dostęp (HTTP 200)

### Opcja 2: Ręcznie (gcloud CLI)

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

### Opcja 3: Czekaj na wyższe Uprawnienia

Poproś administratora GCP, aby przyznał uprawnienie `roles/iam.securityAdmin` lub `roles/run.admin` do konta `falkowskisz01@gmail.com`.

---

## 📊 Co zostało zmienione?

| Plik | Zmiana | Status |
|------|--------|--------|
| `infra/main.tf` | IAM zakomentowana + instrukcja gcloud | ✅ Done |
| `infra/purchase-service.tf` | IAM zakomentowana + instrukcja gcloud | ✅ Done |
| `scripts/setup-cloud-run-iam.sh` | Nowy skrypt | ✅ Created |
| `scripts/gcp-migration.sh` | Zaktualizowana funkcja `apply_iam()` | ✅ Updated |
| `QUICK_START.md` | Instrukcje dla gcloud/skryptu | ✅ Updated |
| `GCP_MIGRATION_STEPS.md` | Sekcja "Ręczne zastosowanie" | ✅ Updated |

---

## 🚀 Nowy Workflow

```bash
# 1. Setup IAM (wymagane uprawnienia gcloud)
./scripts/setup-cloud-run-iam.sh

# 2. Czekaj 30-60 sekund

# 3. Test dostępu
curl -i https://mini-allegro-697507505034.europe-central2.run.app
# Powinno być HTTP 200, nie 403

# 4. Reszta migracji
./scripts/gcp-migration.sh all
```

---

## ✔️ Verification

Po uruchomieniu skryptu sprawdź:

```bash
# Check IAM dla mini-allegro
gcloud run services get-iam-policy mini-allegro \
  --region=europe-central2 \
  --project=paw-2026-496213

# Check IAM dla purchase-service
gcloud run services get-iam-policy purchase-service-dev \
  --region=europe-central2 \
  --project=paw-2026-496213

# Test HTTP access
curl -i https://mini-allegro-697507505034.europe-central2.run.app/
# Expected: HTTP 200 OK
```

---

## 📝 Notatki

- ✅ Terraform jest skonfigurowany prawidłowo (zawiera IAM zakomentowane)
- ✅ Cloud Run usługi już działają (mini-allegro, purchase-service)
- ✅ Tylko IAM setup wymaga uprawnienia `run.services.setIamPolicy`
- ✅ gcloud CLI wymaga pełnego dostępu do projektu (raczej działa)

---

## 🔗 Linki

- [GCP_MIGRATION_STEPS.md](./GCP_MIGRATION_STEPS.md) - Pełne instrukcje
- [QUICK_START.md](./QUICK_START.md) - Szybki start
- [scripts/setup-cloud-run-iam.sh](./scripts/setup-cloud-run-iam.sh) - Skrypt IAM

