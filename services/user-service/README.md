# User Service

Microservice for managing users in mini-allegro. Built with FastAPI and Neo4J.

## Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** Neo4J
- **Docker:** Multi-stage build

## Local Development

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)

### Running Locally (with Docker Compose)

```bash
cd services/user-service

# Start both Neo4J and user-service
./run-local.sh start

# Check health
curl http://localhost:8081/

# List users
curl http://localhost:8081/users

# Get user by ID
curl http://localhost:8081/users/1

# Create user
curl -X POST http://localhost:8081/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "firstName": "New",
    "lastName": "User",
    "roles": ["ROLE_CUSTOMER"]
  }'
```

### Access Neo4J Browser

```
http://localhost:7474
Username: neo4j
Password: testpassword
```

### View Logs

```bash
./run-local.sh logs           # user-service logs
./run-local.sh logs-neo4j     # Neo4J logs
```

### Stop Services

```bash
./run-local.sh stop
```

## API Endpoints

### Health Check
- `GET /` - Returns service health status

### Users
- `GET /users` - List all users
- `GET /users/{id}` - Get user by ID
- `POST /users` - Create new user
- `GET /users-super` - List users with super seller status

## Database Schema (Neo4J)

```cypher
// User node
CREATE (u:User {id: 1, email: "john@example.com", firstName: "John", lastName: "Doe"})

// Role relationship
CREATE (u)-[:HAS_ROLE {name: "ROLE_CUSTOMER"}]->(r:Role)

// SuperSeller relationship (optional)
CREATE (u)-[:IS_SUPER_SELLER]->(s:SuperSeller {id: 1})
```

## Environment Variables

- `PORT` - Server port (default: 8080)
- `NEO4J_URI` - Neo4J connection URI (default: neo4j://localhost:7687)
- `NEO4J_USERNAME` - Neo4J username (default: neo4j)
- `NEO4J_PASSWORD` - Neo4J password

## Deployment

### Cloud Run

```bash
gcloud run deploy user-service-dev \
  --source . \
  --region europe-central2 \
  --allow-unauthenticated \
  --set-env-vars "NEO4J_URI=neo4j://...,NEO4J_USERNAME=neo4j,NEO4J_PASSWORD=..."
```

### Terraform

See `infra/user-service.tf` for full infrastructure configuration.

## Testing

Run integration tests from the project root:

```bash
python -m pytest integ-tests/test_users.py -v
```
