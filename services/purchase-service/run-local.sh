#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="purchase-service"
CONTAINER_NAME="purchase-service"

if [ "${1-}" = "stop" ]; then
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
  exit 0
fi

if [ "${1-}" = "logs" ]; then
  docker logs -f "$CONTAINER_NAME"
  exit 0
fi

docker build -t "$IMAGE_NAME" .

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

docker run -d --name "$CONTAINER_NAME" \
  -e PORT=8080 \
  -p 8081:8080 \
  "$IMAGE_NAME"

echo "Service running at http://localhost:8081"
