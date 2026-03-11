# Zadanie: Symfony CRUD API na Google Cloud Run

## Cel zadania

Stworzenie prostego REST API w Symfony 7 zwracającego dummy data i wdrożenie go na Google Cloud Run przy użyciu Terraform. Projekt ma demonstrować umiejętność tworzenia bezstanowej aplikacji cloudowej z Infrastructure as Code.

## Wymagania techniczne

### Stack technologiczny
- **Framework**: Symfony 7 (PHP 8.3)
- **Container**: Docker (multi-stage build: dev + prod)
- **Cloud**: Google Cloud Run
- **IaC**: Terraform >= 1.0
- **Rejestr obrazów**: Google Artifact Registry

### Architektura projektu
```
nazwa-projektu/
├── services/              # Kod aplikacji Symfony
│   ├── src/
│   │   ├── Controller/
│   │   │   └── OfferController.php
│   │   ├── Entity/
│   │   │   └── Offer.php
│   │   └── Kernel.php
│   ├── config/
│   │   ├── bundles.php
│   │   ├── packages/
│   │   ├── routes.yaml
│   │   └── services.yaml
│   ├── public/
│   │   └── index.php
│   ├── composer.json
│   ├── Dockerfile          # Multi-stage (dev/prod)
│   ├── docker-compose.yml
│   └── .gcloudignore
└── infra/                 # Terraform IaC
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── README.md
    └── global.auto.tfvars -> ../../global/terraform.tfvars
```

## Specyfikacja aplikacji

### 1. Endpoint REST API

**Adres**: `GET /offers`

**Odpowiedź** (JSON):
```json
[
  {
    "id": null,
    "title": "some_title_abc123",
    "description": "some_description_abc123"
  },
  {
    "id": null,
    "title": "some_title_def456",
    "description": "some_description_def456"
  }
]
```

### 2. Klasa Offer (Entity)

```php
<?php

namespace App\Entity;

class Offer
{
    private ?int $id = null;
    private string $title;
    private string $description;

    public function __construct()
    {
        // Generuj losowe wartości przy każdym utworzeniu
        $this->title = 'some_title_' . bin2hex(random_bytes(4));
        $this->description = 'some_description_' . bin2hex(random_bytes(4));
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'description' => $this->description,
        ];
    }

    // gettery i settery dla title i description
}
```

### 3. Kontroler

```php
<?php

namespace App\Controller;

use App\Entity\Offer;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    #[Route('', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $offers = [new Offer(), new Offer()];
        
        return $this->json(
            array_map(fn(Offer $offer) => $offer->toArray(), $offers),
            Response::HTTP_OK,
            [],
            ['json_encode_options' => JSON_PRESERVE_ZERO_FRACTION]
        );
    }
}
```

### 4. Konfiguracja bundles (config/bundles.php)

**UWAGA**: Tylko FrameworkBundle, bez Doctrine/MakerBundle w produkcji!

```php
<?php

return [
    Symfony\Bundle\FrameworkBundle\FrameworkBundle::class => ['all' => true],
];
```

## Dockerfile (Multi-stage)

### Wymagania:
1. **Base image**: `dunglas/frankenphp:php8.3-alpine`
2. **Dwa stage**: `dev` i `prod`
3. **PHP extensions**: `pdo_pgsql`, `opcache`, `intl`, `zip`
4. **Composer**: instalacja przez `COPY --from=composer:2`
5. **Port**: 8080
6. **Prod optimizations**:
   - `php.ini-production`
   - OPcache włączony
   - `composer install --no-dev`
   - `composer dump-autoload --optimize --classmap-authoritative`
   - `php bin/console cache:warmup`

### Uwaga o platformach:
```bash
# Na Apple Silicon (ARM) buduj dla AMD64:
docker buildx build --platform linux/amd64 --target prod \
  -t REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE_NAME:latest --push .
```

## Terraform Infrastructure

### main.tf - Wymagane zasoby:

1. **Provider**:
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}
```

2. **Artifact Registry**:
```hcl
resource "google_artifact_registry_repository" "nazwa_projektu" {
  repository_id = "nazwa-repo"
  location      = var.region
  format        = "DOCKER"
  description   = "Docker repository for nazwa-projektu"
}
```

3. **Cloud Run Service**:
```hcl
resource "google_cloud_run_v2_service" "nazwa_projektu" {
  name     = var.service_name
  location = var.region
  deletion_protection = false

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.nazwa_projektu.repository_id}/${var.service_name}:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }

      env {
        name  = "APP_ENV"
        value = "prod"
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}
```

4. **IAM - Publiczny dostęp**:
```hcl
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.nazwa_projektu.location
  name     = google_cloud_run_v2_service.nazwa_projektu.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### variables.tf
```hcl
variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "nazwa-projektu"
}
```

### outputs.tf
```hcl
output "service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.nazwa_projektu.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.nazwa_projektu.repository_id}"
}
```

## Proces wdrożenia (krok po kroku)

### 1. Przygotowanie środowiska

```bash
# Enable wymaganych API w GCP
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

# Uwierzytelnienie Docker z Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 2. Deployment

```bash
# Krok 1: Terraform - stwórz Artifact Registry
cd infra
terraform init
terraform apply  # Utworzy repozytorium

# Krok 2: Build i push obrazu Docker
cd ../services
docker buildx build --platform linux/amd64 --target prod \
  -t us-central1-docker.pkg.dev/PROJEKT_ID/REPO/APP:latest --push .

# Krok 3: Deploy Cloud Run
cd ../infra
terraform apply  # Wdroży serwis
```

### 3. Weryfikacja

```bash
# Pobierz URL serwisu
terraform output service_url

# Test endpoint
curl $(terraform output -raw service_url)/offers
```

**Oczekiwany output**:
```json
[{"id":null,"title":"some_title_a1b2c3","description":"some_description_a1b2c3"},{"id":null,"title":"some_title_d4e5f6","description":"some_description_d4e5f6"}]
```

## Pliki konfiguracyjne

### .gcloudignore
```
.git
.gitignore
vendor/
var/cache/
var/log/
docker-compose.yml
Dockerfile
README.md
.env.local
.env.*.local
```

### composer.json (najważniejsze sekcje)
```json
{
    "require": {
        "php": ">=8.3",
        "symfony/console": "7.0.*",
        "symfony/framework-bundle": "7.0.*",
        "symfony/runtime": "7.0.*",
        "symfony/yaml": "7.0.*"
    },
    "config": {
        "audit": {
            "block-insecure": false
        }
    }
}
```

## Częste problemy i rozwiązania

### Problem 1: MakerBundle w production
**Objaw**: `ClassNotFoundError: Attempted to load class "MakerBundle"`

**Rozwiązanie**: Usuń Doctrine i MakerBundle z `config/bundles.php` dla środowiska produkcyjnego. Zostaw tylko FrameworkBundle.

### Problem 2: ARM64 vs AMD64
**Objaw**: `Container manifest type 'application/vnd.oci.image.index.v1+json' must support amd64/linux`

**Rozwiązanie**: Użyj `--platform linux/amd64` przy budowaniu obrazu:
```bash
docker buildx build --platform linux/amd64 --target prod ...
```

### Problem 3: Image not found
**Objaw**: `Error code 5, message: Image ... not found`

**Rozwiązanie**: 
1. Najpierw `terraform apply` (tworzy Artifact Registry)
2. Potem `docker push`
3. Na końcu ponownie `terraform apply` (tworzy Cloud Run)

### Problem 4: Composer not found
**Objaw**: `/bin/sh: composer: not found`

**Rozwiązanie**: Dodaj w Dockerfile PRZED użyciem composera:
```dockerfile
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
```

## Kryteria oceny

- ✅ **Działający endpoint** `/offers` zwracający dummy data (2 obiekty)
- ✅ **Terraform IaC** - wszystkie zasoby zdefiniowane deklaratywnie
- ✅ **Multi-stage Dockerfile** - oddzielne stage dev i prod
- ✅ **Cloud Run deployment** - aplikacja dostępna publicznie
- ✅ **Struktura projektu** - services/ + infra/ zgodnie ze specyfikacją
- ✅ **Dokumentacja** - README.md w infra/ z instrukcjami deployment

## Szacowany koszt

**Google Cloud Run Free Tier**:
- 2 miliony requestów/miesiąc
- 360,000 GiB-sekund pamięci
- 180,000 vCPU-sekund

**Dla testów**: ~$0-1/miesiąc (w ramach free tier)

## Materiały pomocnicze

- **Symfony Docs**: https://symfony.com/doc/current/index.html
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Terraform Google Provider**: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- **Dockerfile Best Practices**: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

## Termin i forma oddania

Prześlij:
1. **Link do repozytorium Git** z kodem projektu
2. **URL działającego endpointu** Cloud Run (testowany przez `curl`)
3. **Screenshot** z Terraform output pokazujący `service_url`

---

**Powodzenia!** 🚀

*Pamiętaj: To jest zadanie demonstracyjne z dummy data. W prawdziwym projekcie dodałbyś bazę danych (Cloud SQL/Firestore) i pełny CRUD.*
