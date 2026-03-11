# Zadanie 3.1: Mini Allegro - Symfony CRUD

## Cel
Zbudować "mini Allegro" - od lokalnego developmentu przez deployment na Google Cloud Run.

---

## Etapy zadania

| Etap | Co robimy | Efekt |
|------|-----------|-------|
| 1 | Symfony + Docker lokalnie | Działający projekt z bazą PostgreSQL |
| 2 | Wersja bez bazy (dummy data) | Prostsza wersja do deployu |
| 3 | Deploy na Cloud Run | Aplikacja dostępna publicznie |
| 4 | Więcej encji + baza w chmurze | Pełna wersja z Cloud SQL |

---

## Etap 1: Symfony lokalnie z bazą danych

### Setup projektu

Użyj GitHub Copilot (Cmd+I / Ctrl+I) z promptem:

```
Stwórz projekt Symfony 7 z PHP 8.3 - prosty CRUD API.

Wymagania:
- Symfony 7 skeleton (API only, bez Twig)
- Doctrine ORM z PostgreSQL
- Docker + docker-compose.yml dla lokalnego developmentu
- Encja Offer: id, title, description, price, createdAt, updatedAt
- CRUD endpoints: GET/POST/PUT/DELETE /offers

Docker:
- app (PHP + Symfony)
- database (PostgreSQL 15)
- volume mount dla kodu (live reload)
```

### Uruchom

```bash
docker compose up -d
docker compose exec app composer install
docker compose exec app php bin/console doctrine:migrations:migrate
```

### Przetestuj

```bash
# Dodaj ofertę
curl -X POST http://localhost:8080/offers \
  -H "Content-Type: application/json" \
  -d '{"title": "iPhone 15", "price": 4999.99}'

# Lista ofert
curl http://localhost:8080/offers
```

### Checkpoint Etap 1
- [ ] `docker compose ps` - kontenery działają
- [ ] Endpoint `/offers` zwraca dane
- [ ] Dane zapisują się w bazie

---

## Etap 2: Wersja bez bazy (dummy data)

Cloud Run preferuje stateless aplikacje. Zrobimy uproszczoną wersję.

### Zmodyfikuj kontroler

Zamiast Doctrine - zwracaj dummy data:

```php
#[Route('/offers', methods: ['GET'])]
public function index(): JsonResponse
{
    $offers = [
        new Offer('iPhone 15', 'Nowy, zafoliowany', 4999.99),
        new Offer('MacBook Pro', '16 cali, M3', 12999.99),
    ];

    return $this->json(
        array_map(fn($o) => $o->toArray(), $offers)
    );
}
```

### Uproszczona encja (bez Doctrine)

```php
class Offer
{
    public function __construct(
        private string $title,
        private string $description,
        private float $price
    ) {}

    public function toArray(): array
    {
        return [
            'title' => $this->title,
            'description' => $this->description,
            'price' => $this->price,
        ];
    }
}
```

### Usuń Doctrine z bundles.php

```php
return [
    Symfony\Bundle\FrameworkBundle\FrameworkBundle::class => ['all' => true],
    // Zakomentuj lub usuń DoctrineBundle
];
```

### Przetestuj lokalnie

```bash
docker compose up --build
curl http://localhost:8080/offers
```

### Checkpoint Etap 2
- [ ] Aplikacja działa bez bazy danych
- [ ] Endpoint `/offers` zwraca dummy data

---

## Etap 3: Deploy na Google Cloud Run

### Przygotuj Dockerfile produkcyjny

Zobacz [pomoc_symfony_cloud_run.md](./pomoc_symfony_cloud_run.md) - zawiera gotowy Dockerfile i konfigurację Terraform.

### Kroki deployu

```bash
# 1. Włącz API (jednorazowo)
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# 2. Uwierzytelnij Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# 3. Terraform - stwórz Artifact Registry
cd infra
terraform init
terraform apply

# 4. Build i push obrazu (na Apple Silicon dodaj --platform linux/amd64)
cd ../services
docker buildx build --platform linux/amd64 --target prod \
  -t us-central1-docker.pkg.dev/PROJECT_ID/REPO/APP:latest --push .

# 5. Deploy Cloud Run
cd ../infra
terraform apply
```

### Przetestuj

```bash
curl $(terraform output -raw service_url)/offers
```

### Checkpoint Etap 3
- [ ] Obraz w Artifact Registry
- [ ] Cloud Run service działa
- [ ] Publiczny URL zwraca JSON

---

## Etap 4: Więcej encji + baza w chmurze

### Dodaj swoją encję

Prowadzący przydzieli Ci jedną:

| Encja | Pola |
|-------|------|
| `User` | email, name, type (buyer/seller) |
| `Category` | name, slug, parentId |
| `Order` | offerId, buyerId, quantity, totalPrice, status |
| `Review` | orderId, rating (1-5), comment |
| `Address` | userId, street, city, postalCode |
| `Cart` | userId |

### Utwórz branch i PR

```bash
git checkout -b feature/[twoja-encja]
# ... dodaj kod ...
git commit -m "Add [Encja] entity"
git push -u origin feature/[twoja-encja]
```

### Podłącz Cloud SQL (opcjonalnie)

Jeśli starczy czasu, podłączymy wspólną bazę Cloud SQL:
- Terraform tworzy instancję
- Wszystkie serwisy łączą się do tej samej bazy
- Doświadczycie problemów "integracji przez bazę"

### Checkpoint Etap 4
- [ ] Twoja encja dodana
- [ ] PR utworzony i zreviewowany
- [ ] Merge do main

---

## Materiały pomocnicze

- [pomoc_symfony_cloud_run.md](./pomoc_symfony_cloud_run.md) - szczegółowa instrukcja z Dockerfile, Terraform, rozwiązywaniem problemów

---

## Rozwiązywanie problemów

### Port 8080 zajęty
```bash
lsof -i :8080
```

### Kontener nie wstaje
```bash
docker compose down -v
docker compose up --build
```

### ARM64 vs AMD64 (Apple Silicon)
```bash
docker buildx build --platform linux/amd64 ...
```

### Image not found w Cloud Run
Kolejność: Terraform (Artifact Registry) → Docker push → Terraform (Cloud Run)
