#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="symfony-purchase"
CONTAINER_NAME="symfony-purchase-local"

build_and_run() {
  cd "$ROOT_DIR"
  docker build -t "$IMAGE_NAME" --target prod .

  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker rm -f "$CONTAINER_NAME" >/dev/null
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8082:8080 \
    -e PORT=8080 \
    -e APP_ENV=dev \
    -e APP_SECRET=0123456789abcdef0123456789abcdef \
    -e PURCHASE_SERVICE_URL=http://host.docker.internal:8081 \
    "$IMAGE_NAME" >/dev/null

  echo "Service running at http://localhost:8082"
}

stop_container() {
  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker rm -f "$CONTAINER_NAME" >/dev/null
    echo "Stopped ${CONTAINER_NAME}"
  else
    echo "Container ${CONTAINER_NAME} is not running"
  fi
}

show_logs() {
  docker logs -f "$CONTAINER_NAME"
}

case "${1:-}" in
  "")
    build_and_run
    ;;
  stop)
    stop_container
    ;;
  logs)
    show_logs
    ;;
  *)
    echo "Usage: ./run-local.sh [stop|logs]"
    exit 1
    ;;
esac
