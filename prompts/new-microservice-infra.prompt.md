---
mode: agent
description: "Tworzy infrastrukturę Terraform i GitHub Actions workflow dla nowego mikroserwisu w tym projekcie"
---

Jesteś agentem pracującym w tym repozytorium. Stwórz infrastrukturę i pipeline CI/CD dla nowego mikroserwisu.

## Dane wejściowe (wypełnij przed uruchomieniem)

- **Nazwa serwisu**: `<SERVICE_NAME>` (np. `orders-service`, `payments-service`)
- **Port aplikacji**: `<PORT>` (np. `8082`)
- **Nazwa brancha roboczego**: `<BRANCH_NAME>` (np. `km-orders-service`)

## Zadanie

### 1. Terraform — `infra/<SERVICE_NAME>/`

Stwórz trzy pliki wzorując się na `infra/products-service/`:

- **`main.tf`** — `google_cloud_run_v2_service` z podanym portem + `google_cloud_run_v2_service_iam_member` (allUsers, roles/run.invoker). Backend GCS z `backend "gcs" {}`.
- **`variables.tf`** — zmienne: `project` (default: `project-f5f4f6f0-acae-485b-a16`), `region` (default: `europe-central2`), `service_name` (default: `<SERVICE_NAME>-dev`), `image`.
- **`outputs.tf`** — output `service_url` z URI Cloud Run.

### 2. GitHub Actions — `.github/workflows/deploy-<SERVICE_NAME>.yml`

Stwórz osobny workflow wzorując się na `.github/workflows/deploy-products-service.yml`:

- **Trigger**: push na `develop` oraz tymczasowo na `<BRANCH_NAME>` (z komentarzem `# TODO: usunąć przed mergem`) gdy zmieniły się pliki w `services/<SERVICE_NAME>/**`, `infra/<SERVICE_NAME>/**` lub sam plik workflow.
- **env**: `PROJECT_ID`, `REGION`, `REGISTRY`, `REPOSITORY` takie same jak w istniejących workflowach. `IMAGE` i `SERVICE_DEV` dostosuj do nazwy serwisu.
- **Jobs** w kolejności:
  1. `validate-secrets` — sprawdź `GCP_SA_KEY` i `TF_STATE_BUCKET`
  2. `build` — zbuduj i pushuj obraz Docker z `services/<SERVICE_NAME>/Dockerfile` do Artifact Registry (`mini-allegro` repo), output: `image_tag`
  3. `terraform` — `terraform init` z backendem `bucket=$TF_STATE_BUCKET`, `prefix=<SERVICE_NAME>/dev`, następnie `terraform apply -var="image=<image_tag>"`
  4. `deploy` — `google-github-actions/deploy-cloudrun@v2`, po deploy health check `GET /<SERVICE_NAME_PATH>` (dopytaj użytkownika o ścieżkę health check jeśli nie jest oczywista)

### 3. Po wygenerowaniu

Podaj użytkownikowi gotowe polecenia do lokalnego testowania Terraform:

```bash
cd infra/<SERVICE_NAME>
terraform init \
  -backend-config="bucket=mini-allegro-tf-state" \
  -backend-config="prefix=<SERVICE_NAME>/dev"

terraform plan \
  -var="image=europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/<SERVICE_NAME>:test"
```

## Ważne zasady

- Nie modyfikuj istniejących plików terraform ani workflows
- Trzymaj styl i konwencje istniejących plików w repozytorium
- Serwis jest bezstanowy (bez bazy danych) — nie dodawaj żadnych zasobów SQL
- Każdy serwis ma osobny prefix stanu Terraform: `<SERVICE_NAME>/dev`
- Plik workflow ma być w osobnym pliku — nie rozszerzaj `deploy.yml`
