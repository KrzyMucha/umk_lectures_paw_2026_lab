#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="purchase-service"
CONTAINER_NAME="purchase-service-local"

build_and_run() {
  cd "$ROOT_DIR"
  docker build -t "$IMAGE_NAME" .

  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker rm -f "$CONTAINER_NAME" >/dev/null
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8081:8080 \
    -e PORT=8080 \
    "$IMAGE_NAME" >/dev/null

  echo "Service running at http://localhost:8081"
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
