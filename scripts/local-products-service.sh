#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/products-service"

export PORT="${PORT:-8081}"

echo "Starting products-service on http://localhost:$PORT ..."
echo "  GET  /products"
echo "  POST /products"
echo ""
echo "Press Ctrl+C to stop."
echo ""

cd "$SERVICE_DIR"
sbt run
