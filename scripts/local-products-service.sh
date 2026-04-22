#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/products-service"

export PORT="${PORT:-8081}"

# Załaduj .env z katalogu serwisu jeśli istnieje
ENV_FILE="$SERVICE_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is required."
  echo "  Utwórz plik services/products-service/.env z zawartością:"
  echo "  DATABASE_URL=postgresql://user:pass@host:5432/mini_allegro_dev"
  exit 1
fi

echo "Starting products-service on http://localhost:$PORT ..."
echo "  GET  /products"
echo "  POST /products"
echo ""
echo "Press Ctrl+C to stop."
echo ""

cd "$SERVICE_DIR"
sbt run
