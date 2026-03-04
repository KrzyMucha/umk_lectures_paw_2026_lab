# Zadanie 2.1: Hello Team

## Cel
Poznanie GCP Console i Terraform poprzez stworzenie zespołowego "Hello Team" - każdy student tworzy swoją Cloud Function, razem tworzą całość.

## Czas
~60 minut (25 min Console + 35 min Terraform)

## Wymagania wstępne
- Konto Google z dostępem do projektu `paw-2026`
- Zainstalowane: gcloud CLI, Terraform, Git, VS Code
- Sklonowane repo projektu

---

## Część 1: Cloud Function przez Console (~25 min)

### Krok 1: Logowanie do GCP
1. Wejdź na https://console.cloud.google.com
2. Zaloguj się kontem Google (tym które ma dostęp do projektu)
3. Wybierz projekt `paw-2026` (góra strony)

### Krok 2: Przejście do Cloud Functions
1. Menu (hamburger) → Cloud Functions
2. Jeśli API nie jest włączone, kliknij "Enable"

### Krok 3: Tworzenie funkcji
1. Kliknij **Create Function**
2. Wypełnij:
   - **Environment**: 2nd gen
   - **Function name**: `hello-{twoje-imie}` (np. `hello-anna`)
   - **Region**: `europe-central2` (Warszawa)
   - **Trigger type**: HTTPS
   - **Authentication**: Allow unauthenticated invocations

3. Kliknij **Next**

### Krok 4: Kod funkcji
1. **Runtime**: Node.js 20
2. **Entry point**: `handler`
3. Zamień kod w `index.js` na:

```javascript
const functions = require('@google-cloud/functions-framework');

functions.http('handler', (req, res) => {
  const response = {
    message: 'Hello from {Twoje Imię}!',
    team: 'Zespół {N}',
    timestamp: new Date().toISOString()
  };
  res.json(response);
});
```

4. Upewnij się, że `package.json` zawiera:
```json
{
  "name": "hello-function",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "@google-cloud/functions-framework": "^3.0.0"
  }
}
```

### Krok 5: Deploy i test
1. Kliknij **Deploy**
2. Poczekaj ~2 minuty na deployment
3. Po deploymencie kliknij na nazwę funkcji
4. Skopiuj **URL** z zakładki "Trigger"
5. Otwórz URL w przeglądarce - powinieneś zobaczyć JSON z odpowiedzią

### Checkpoint
- [ ] Funkcja jest widoczna w Cloud Functions
- [ ] URL zwraca JSON z Twoim imieniem
- [ ] Status: Active (zielona ikona)

---

## Część 2: Cloud Function przez Terraform (~35 min)

### Krok 1: Przygotowanie
1. Otwórz terminal
2. Przejdź do sklonowanego repo:
```bash
cd paw-2026
git pull origin main
```

### Krok 2: Struktura projektu
Sprawdź strukturę:
```
paw-2026/
├── infrastructure/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── services/
│   └── hello-team/
│       ├── functions/
│       │   └── ... (tu dodasz swój plik)
│       └── src/
│           └── hello/
│               ├── index.js
│               └── package.json
└── README.md
```

### Krok 3: Utwórz plik Terraform dla swojej funkcji
1. Utwórz plik `services/hello-team/functions/{twoje-imie}.tf`
2. Wpisz (zamień `{imie}` na swoje):

```hcl
# Hello function for {Imię}
resource "google_cloudfunctions2_function" "hello_{imie}" {
  name        = "hello-{imie}"
  location    = var.region
  description = "Hello from {Imię} - Zespół {N}"

  build_config {
    runtime     = "nodejs20"
    entry_point = "handler"
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.hello_source.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "128Mi"
    timeout_seconds    = 60
  }

  labels = {
    team   = "zespol-{n}"
    author = "{imie}"
  }
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "hello_{imie}_public" {
  location = google_cloudfunctions2_function.hello_{imie}.location
  name     = google_cloudfunctions2_function.hello_{imie}.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output URL
output "hello_{imie}_url" {
  value = google_cloudfunctions2_function.hello_{imie}.service_config[0].uri
}
```

### Krok 4: Commit i push
```bash
git add services/hello-team/functions/{imie}.tf
git commit -m "Add hello-{imie} function"
git push origin main
```

### Krok 5: Terraform apply
```bash
cd infrastructure
terraform init    # tylko za pierwszym razem
terraform plan    # sprawdź co się zmieni
terraform apply   # potwierdź "yes"
```

### Krok 6: Usuń funkcję z Console
1. Wróć do GCP Console → Cloud Functions
2. Znajdź swoją funkcję (utworzoną ręcznie w Części 1)
3. Usuń ją (teraz zarządza nią Terraform)

### Checkpoint
- [ ] Plik `.tf` jest w repo
- [ ] `terraform apply` zakończone sukcesem
- [ ] Funkcja działa (ten sam URL lub nowy z output)
- [ ] Funkcja utworzona ręcznie usunięta z Console

---

## Efekt końcowy

Po wykonaniu zadania przez wszystkich studentów:

```
GET /hello-anna   → {"message": "Hello from Anna!", "team": "Zespół 1", ...}
GET /hello-jan    → {"message": "Hello from Jan!", "team": "Zespół 1", ...}
GET /hello-maria  → {"message": "Hello from Maria!", "team": "Zespół 2", ...}
...
```

Wszystkie funkcje:
- Zdefiniowane jako kod (Terraform)
- Wersjonowane w Git
- Łatwe do odtworzenia na nowym koncie GCP

---

## Pytania kontrolne

1. Jaka jest różnica między tworzeniem funkcji przez Console a przez Terraform?
2. Co się stanie jak zrobisz `terraform destroy`?
3. Dlaczego usunęliśmy funkcję utworzoną ręcznie?
4. Jak sprawdzić kto utworzył którą funkcję? (podpowiedź: labels)

---

## Rozwiązywanie problemów

### "Permission denied"
- Sprawdź czy jesteś zalogowany: `gcloud auth list`
- Sprawdź projekt: `gcloud config get-value project`

### "API not enabled"
- Włącz API: `gcloud services enable cloudfunctions.googleapis.com`

### "Terraform state lock"
- Ktoś inny robi `terraform apply` - poczekaj lub skoordynuj się

### "Function already exists"
- Usuń ręcznie utworzoną funkcję z Console przed `terraform apply`
