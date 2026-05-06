# User Service - Setup Guide

Kompletny serwis microservices dla User entity z FastAPI + Neo4J.

## 📋 Co zostało zrobione

### Krok 1: Skeleton serwisu (✅ Zakończone)
- ✅ FastAPI aplikacja z hardkodowanymi danymi
- ✅ Dockerfile z multi-stage build
- ✅ run-local.sh skrypt do uruchomienia lokalnie
- ✅ Health check endpoint
- ✅ REST API endpoints (`GET /users`, `GET /users/{id}`, `POST /users`, `GET /users-super`)

### Krok 2: Infrastruktura GCP (✅ Zakończone)
- ✅ Neo4J na Compute Engine (infra/dev/neo4j.tf, infra/prod/neo4j.tf)
- ✅ Cloud Run services (infra/dev/user-service.tf, infra/prod/user-service.tf)
- ✅ Secret Manager integration dla Neo4J passwords
- ✅ GitHub Actions CI/CD (.github/workflows/deploy.yml)

### Krok 3a: Połączenie z Neo4J lokalnie (✅ Zakończone)
- ✅ database.py - Neo4J driver i repository methods
- ✅ Startup/shutdown event handlers
- ✅ Automatic database initialization (constraints, indexes)
- ✅ Fallback na hardcoded data jeśli baza niedostępna
- ✅ Full CRUD operations dla User nodes

### Krok 3b: Połączenie z Neo4J na Cloud Run (⏳ Ready)
- ✅ Terraform variables ustawione
- ✅ Environment variables w Cloud Run
- ✅ Neo4J instance startup script

### Krok 4: Monolit deleguje do user-service (⏳ Do zrobienia)
- Modyfikacja monolitu Symfony do delegacji `/users` do nowego serwisu

### Krok 5: Testy integracyjne (⏳ Do zrobienia)
- Weryfikacja że wszystkie testy przechodzą

---

## 🚀 Jak uruchomić lokalnie

### Prerequisyty

```bash
# Python 3.11+
python --version

# Docker (do Neo4J)
docker --version
```

### 1. Zainstaluj zależności

```bash
cd services/user-service
pip install -r requirements.txt
```

### 2. Uruchom Neo4J w Dockerze

```bash
# Start Neo4J container
docker run -d \
  --name neo4j-local \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/testpassword \
  neo4j:5.15-community

# Lub użyj skryptu
./run-local.sh
```

### 3. Ustaw zmienne środowiskowe

```bash
export NEO4J_URI="neo4j://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="testpassword"
export PORT=8080
```

### 4. Uruchom serwis

```bash
# Opcja A: Lokalnie (bez Docker)
python main.py

# Opcja B: W Docker (zalecane)
./run-local.sh
```

### 5. Testuj API

```bash
# Health check
curl http://localhost:8081/

# List users
curl http://localhost:8081/users | python3 -m json.tool

# Get user by ID
curl http://localhost:8081/users/1

# Create user
curl -X POST http://localhost:8081/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "firstName": "Alice",
    "lastName": "Wonder",
    "roles": ["ROLE_CUSTOMER", "ROLE_SELLER"]
  }'
```

### 6. Obejrzyj Neo4J Browser

Otwórz w przeglądarce: `http://localhost:7474/browser/`
- Username: `neo4j`
- Password: `testpassword`

Query do zobaczenia wszystkich userów:
```cypher
MATCH (u:User)-[r:HAS_ROLE]->(role:Role)
RETURN u, role
LIMIT 25
```

---

## 🔧 Konfiguracja Terraformu

### DEV Environment

```bash
cd infra/dev
export TF_VAR_neo4j_initial_password="twoje-haslo"
export TF_VAR_neo4j_password="twoje-haslo"

terraform init \
  -backend-config="bucket=YOUR_TF_STATE_BUCKET" \
  -backend-config="prefix=mini-allegro/dev"

terraform plan
terraform apply
```

### PROD Environment

```bash
cd infra/prod
export TF_VAR_neo4j_initial_password="silne-haslo"
export TF_VAR_neo4j_password="silne-haslo"

terraform init \
  -backend-config="bucket=YOUR_TF_STATE_BUCKET" \
  -backend-config="prefix=mini-allegro/prod"

terraform plan
terraform apply
```

---

## 📊 Struktura Neo4J

### Nodes

**User**
```cypher
{
  id: Int,
  email: String (UNIQUE),
  firstName: String,
  lastName: String
}
```

**Role**
```cypher
{
  name: String (UNIQUE) - "ROLE_CUSTOMER" | "ROLE_SELLER"
}
```

**SuperSeller** (optional)
```cypher
{
  id: Int (UNIQUE)
}
```

### Relationships

- `(User)-[:HAS_ROLE]->(Role)` - User ma rolę
- `(User)-[:IS_SUPER_SELLER]->(SuperSeller)` - User jest super sprzedawcą

### Cypher Queries

```cypher
# Utworz usera
CREATE (u:User {id: 1, email: "john@example.com", firstName: "John", lastName: "Doe"})
WITH u
MERGE (r:Role {name: "ROLE_CUSTOMER"})
CREATE (u)-[:HAS_ROLE]->(r)

# Pobierz usera z rolami
MATCH (u:User {id: 1})-[r:HAS_ROLE]->(role:Role)
RETURN u, collect(role.name) AS roles

# Pobierz super sprzedawców
MATCH (u:User)-[:IS_SUPER_SELLER]->(ss:SuperSeller)
RETURN u, ss

# Usuń usera
MATCH (u:User {id: 1})
DETACH DELETE u
```

---

## 🔐 GitHub Secrets

Dodaj do GitHub repository secrets:

| Secret | Wartość |
|--------|---------|
| `GCP_SA_KEY` | JSON service account key |
| `TF_STATE_BUCKET` | Bucket name dla Terraform state |
| `DEV_DATABASE_URL` | PostgreSQL connection string (dla monolitu) |
| `APP_SECRET` | Tajny klucz dla aplikacji |
| `NEO4J_PASSWORD` | Hasło do Neo4J (np. `SecurePass123!`) |

---

## 🐛 Troubleshooting

### Neo4J Connection Refused

```bash
# Check if Neo4J container is running
docker ps | grep neo4j

# View logs
docker logs neo4j-local

# Restart
docker restart neo4j-local
```

### Health Check Shows "disconnected"

```bash
# Sprawdź zmienne środowiskowe
echo $NEO4J_URI
echo $NEO4J_USERNAME

# Spróbuj połączyć się bezpośrednio z Neo4J
cypher-shell -a "neo4j://localhost:7687" -u neo4j -p testpassword "RETURN 1"
```

### Dockerfile Build Error

```bash
# Wyczyść cache Docker
docker system prune -a

# Rebuild
cd services/user-service
docker build -t user-service:test .
```

---

## 📦 API Endpoints

### Health

- **GET** `/` - Health check
  ```json
  {
    "status": "ok",
    "service": "user-service",
    "database": "connected"
  }
  ```

### Users

- **GET** `/users` - List all users
  ```json
  [
    {
      "id": 1,
      "email": "john@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "roles": ["ROLE_CUSTOMER"]
    }
  ]
  ```

- **GET** `/users/{id}` - Get user by ID
  ```json
  {
    "id": 1,
    "email": "john@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "roles": ["ROLE_CUSTOMER"]
  }
  ```

- **POST** `/users` - Create new user
  ```json
  {
    "email": "alice@example.com",
    "firstName": "Alice",
    "lastName": "Wonder",
    "roles": ["ROLE_CUSTOMER"]
  }
  ```

- **GET** `/users-super` - List users with super seller status
  ```json
  [
    {
      "id": 2,
      "email": "jane@example.com",
      "firstName": "Jane",
      "lastName": "Smith",
      "roles": ["ROLE_SELLER"],
      "superSellerId": 1
    }
  ]
  ```

---

## 🔄 CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/deploy.yml`):

1. **validate-secrets** - Sprawdza czy wszystkie required sekrety są ustawione
2. **build-user-service-dev** - Buduje Docker image dla user-service
3. **terraform-dev** - Deployuje infrastrukturę (Neo4J VM, Cloud Run)
4. **build-dev** - Buduje image dla monolitu
5. **deploy-dev** - Deployuje monolit na Cloud Run
6. **integration-tests-dev** - Uruchamia testy integracyjne
7. **promote-to-main** - Auto-merge develop → main

---

## 📝 Next Steps

### Krok 4: Modyfikacja Monolitu

Zmień `UserController.php` w monolicie aby delegować requesty do nowego serwisu:

```php
#[Route('/users', methods: ['GET'])]
public function index(): JsonResponse
{
    $userServiceUrl = $_ENV['USER_SERVICE_URL'];
    $response = $httpClient->request('GET', "$userServiceUrl/users");
    return $this->json(json_decode($response->getContent()));
}
```

### Krok 5: Testy Integracyjne

Wszystkie testy z `integ-tests/test_users.py` powinny przechodzić:

```bash
cd services/symphony-monolith
pytest ../../integ-tests/test_users.py -v
```

---

## 📚 Dodatkowe Materiały

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Neo4J Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

---

## ✅ Checklist Deployment'u

- [ ] NEO4J_PASSWORD secret dodany do GitHub
- [ ] Terraform variables ustawione (`TF_STATE_BUCKET`, `GCP_SA_KEY`)
- [ ] Push do `develop` branch trigguje CI/CD
- [ ] Neo4J VM została utworzona na GCP
- [ ] user-service-dev Cloud Run service jest dostępny
- [ ] Monolithe ma zmienną `USER_SERVICE_URL` ustawioną
- [ ] Testy integracyjne przechodzą
- [ ] Merge do `main` działa automatycznie

---

Generated: 2026-04-29
