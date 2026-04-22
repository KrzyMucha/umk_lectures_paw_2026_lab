#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/products-service"
IMAGE="products-service:local"
CONTAINER="products-service-test"
PORT="${PORT:-8081}"
BASE_URL="http://localhost:$PORT"

cleanup() {
  echo ""
  echo "--- Cleaning up ---"
  docker rm -f "$CONTAINER" 2>/dev/null || true
}
trap cleanup EXIT

# --- Build ---
echo "--- Building Docker image ---"
docker build -t "$IMAGE" "$SERVICE_DIR"

# --- Run ---
echo ""
echo "--- Starting container on port $PORT ---"
docker run -d --name "$CONTAINER" -p "$PORT:8081" "$IMAGE"

echo "Waiting for service to be ready..."
for i in $(seq 1 20); do
  if curl -sf "$BASE_URL/products" > /dev/null 2>&1; then
    break
  fi
  if [ "$i" -eq 20 ]; then
    echo "ERROR: Service did not start in time."
    docker logs "$CONTAINER"
    exit 1
  fi
  sleep 1
done

# --- Tests ---
PASS=0
FAIL=0

check() {
  local desc="$1" expected="$2" actual="$3"
  if echo "$actual" | grep -q "$expected"; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    echo "        expected to contain: $expected"
    echo "        got: $actual"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "--- Running tests ---"

# GET /products – zwraca listę
RESPONSE=$(curl -sf "$BASE_URL/products")
check "GET /products returns Laptop Pro"        "Laptop Pro"  "$RESPONSE"
check "GET /products returns USB-C Hub"         "USB-C Hub"   "$RESPONSE"

# POST /products – tworzy produkt
CREATED=$(curl -sf -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Widget","description":"Docker test","price":19.99}')
check "POST /products returns new product name" "Test Widget" "$CREATED"
check "POST /products returns price"            "19.99"       "$CREATED"

# POST /products – brak name → 400
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{"description":"no name","price":5.0}')
check "POST /products without name returns 400" "400" "$STATUS"

# POST /products – brak price → 400
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{"name":"No Price"}')
check "POST /products without price returns 400" "400" "$STATUS"

# GET po dodaniu – nowy produkt widoczny
RESPONSE=$(curl -sf "$BASE_URL/products")
check "GET /products after POST contains new product" "Test Widget" "$RESPONSE"

# --- Summary ---
echo ""
echo "--- Results: $PASS passed, $FAIL failed ---"
[ "$FAIL" -eq 0 ] || exit 1
