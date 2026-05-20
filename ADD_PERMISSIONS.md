# Instrukcja: Dodanie Uprawnień do Cloud Run IAM Setup

**Problem:** `falkowskisz01@gmail.com` nie ma uprawnienia `run.services.setIamPolicy`

---

## 1️⃣ Sprawdź Obecne Uprawnienia

```bash
# Sprawdź jakie role masz na projekcie
gcloud projects get-iam-policy paw-2026-496213 \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:falkowskisz01@gmail.com"
```

**Możliwe output:**
```
ROLE
roles/editor
roles/iam.securityAdmin
roles/owner
...
```

---

## 2️⃣ Dodaj Sobie Uprawnienia

Jeśli jesteś **Project Editor** lub wyżej, możesz sam sobie dodać rolę:

### Opcja A: `roles/run.admin` (Zalecane)
Daje pełny dostęp do Cloud Run:

```bash
gcloud projects add-iam-policy-binding paw-2026-496213 \
  --member=user:falkowskisz01@gmail.com \
  --role=roles/run.admin
```

### Opcja B: `roles/iam.securityAdmin` 
Daje dostęp do setIamPolicy na wszystkim:

```bash
gcloud projects add-iam-policy-binding paw-2026-496213 \
  --member=user:falkowskisz01@gmail.com \
  --role=roles/iam.securityAdmin
```

### Opcja C: Specyficzna rola `roles/run.serviceConsumer`
Jeśli chcesz tylko Cloud Run:

```bash
gcloud projects add-iam-policy-binding paw-2026-496213 \
  --member=user:falkowskisz01@gmail.com \
  --role=roles/run.serviceConsumer
```

---

## 3️⃣ Weryfikacja

```bash
# Sprawdź czy uprawnienia się zastosowały
gcloud projects get-iam-policy paw-2026-496213 \
  --flatten="bindings[].members" \
  --filter="bindings.members:falkowskisz01@gmail.com" \
  --format=table
```

---

## 4️⃣ Odśwież gcloud

```bash
gcloud auth application-default print-access-token > /dev/null
```

---

## 5️⃣ Teraz Spróbuj Ponownie

```bash
./scripts/setup-cloud-run-iam.sh
```

---

## ⚠️ Jeśli To Nie Zadziała

Jeśli nawet `roles/run.admin` nie zadziała, to znaczy że konto nie ma uprawnienia do **edycji IAM na Cloud Run** na poziomie projektu. W takim razie:

### Opcja 1: Cloud Console (GUI)
1. Idź do https://console.cloud.google.com/iam-admin/iam?project=paw-2026-496213
2. Kliknij "Grant Access"
3. Email: `falkowskisz01@gmail.com`
4. Role: `Cloud Run Admin` (roles/run.admin)
5. Save

### Opcja 2: Cloud Run Service - Bezpośrednio

Zamiast `add-iam-policy-binding` na Cloud Run service, możesz jechać przez Cloud Console:

1. https://console.cloud.google.com/run?project=paw-2026-496213
2. Kliknij `mini-allegro`
3. Górny panel → "PERMISSIONS"
4. "Grant Access"
5. `allUsers` → Role: `Cloud Run Invoker`
6. Save

Powtórz dla `purchase-service-dev`.

---

## 📝 Notatki

- `roles/owner` - Ma wszystko
- `roles/editor` - Ma większość, ale NIE `setIamPolicy`
- `roles/run.admin` - Ma dostęp do Cloud Run IAM
- `roles/iam.securityAdmin` - Ma dostęp do wszystkich IAM operacji

Jeśli masz `roles/editor`, to brakuje Ci `iam.securityAdmin`. Dodaj sobie `roles/run.admin` lub idź przez Cloud Console.
