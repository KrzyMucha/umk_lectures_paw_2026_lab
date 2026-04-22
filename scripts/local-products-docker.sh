#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/products-service"
IMAGE="products-service:local"
CONTAINER="products-service-docker"
PORT="${PORT:-8082}"

cleanup() {
  echo ""
  echo "Stopping container..."
  docker rm -f "$CONTAINER" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "--- Building Docker image ---"
docker build -t "$IMAGE" "$SERVICE_DIR"

echo ""
echo "--- Starting products-service (Docker) on http://localhost:$PORT ---"
echo "  GET  /products"
echo "  POST /products"
echo ""
echo "Press Ctrl+C to stop."
echo ""

docker run --rm --name "$CONTAINER" -p "$PORT:8081" "$IMAGE"
