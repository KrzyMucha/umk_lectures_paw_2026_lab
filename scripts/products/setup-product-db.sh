#!/usr/bin/env bash
# Uruchamia lokalny Postgres + pgvector w Dockerze i tworzy schemat produktów.
# Użycie: ./scripts/products/setup-product-db.sh [--reset]
set -euo pipefail

CONTAINER="products-db-local"
DB_PORT=5433
DB_NAME="products_dev"
DB_USER="products"
DB_PASS="products"
IMAGE="pgvector/pgvector:pg16"

DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$ROOT_DIR/services/products-service/.env"
SEED_FILE="$ROOT_DIR/scripts/products/products_seed.json"

# --reset: usuwa istniejący kontener
if [[ "${1:-}" == "--reset" ]]; then
  echo "Usuwam kontener $CONTAINER..."
  docker rm -f "$CONTAINER" 2>/dev/null || true
fi

# Uruchom kontener jeśli nie działa
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "Startuję $CONTAINER (postgres+pgvector na porcie $DB_PORT)..."
  docker run -d \
    --name "$CONTAINER" \
    -e POSTGRES_DB="$DB_NAME" \
    -e POSTGRES_USER="$DB_USER" \
    -e POSTGRES_PASSWORD="$DB_PASS" \
    -p "${DB_PORT}:5432" \
    "$IMAGE"

  echo -n "Czekam na Postgres..."
  for i in $(seq 1 30); do
    if docker exec "$CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" -q 2>/dev/null; then
      echo " gotowy."
      break
    fi
    sleep 1
    echo -n "."
    if [[ $i -eq 30 ]]; then
      echo " TIMEOUT"
      exit 1
    fi
  done
else
  echo "Kontener $CONTAINER już działa."
fi

# Schemat
echo "Tworzę schemat..."
docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" <<'SQL'
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS product (
    id        BIGSERIAL PRIMARY KEY,
    data      JSONB NOT NULL,
    embedding vector(768)
);

-- GIN index do szybkich zapytań JSONB (np. data->>'player' = 'Kobe Bryant')
CREATE INDEX IF NOT EXISTS product_data_gin_idx
    ON product USING gin (data);

-- HNSW index do wyszukiwania wektorowego (cosine similarity)
-- Tworzony nawet bez danych — wypełni się po imporcie embeddingów
CREATE INDEX IF NOT EXISTS product_embedding_hnsw_idx
    ON product USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
SQL

echo "Schemat gotowy."

# Import danych z products_seed.json
if [[ -f "$SEED_FILE" ]]; then
  echo "Importuję produkty z products_seed.json..."
  python3 "$ROOT_DIR/scripts/products/import-products.py" \
    --db-url "$DATABASE_URL" \
    --file "$SEED_FILE"
else
  echo "Brak $SEED_FILE — pomiń import lub uruchom scripts/generate-products.py"
fi

# Zapisz DATABASE_URL do .env serwisu
echo "DATABASE_URL=$DATABASE_URL" > "$ENV_FILE"
echo ""
echo "Gotowe!"
echo "  DATABASE_URL=$DATABASE_URL"
echo "  Kontener:    $CONTAINER"
echo "  Plik .env:   $ENV_FILE"
echo ""
echo "Zatrzymaj DB:  docker stop $CONTAINER"
echo "Usuń i reset:  ./scripts/products/setup-product-db.sh --reset"
