#!/bin/bash

set -e

CONTAINER_NAME="product-review-service"
IMAGE_NAME="product-review-service"

case "${1:-}" in
  stop)
    echo "Stopping $CONTAINER_NAME..."
    docker stop "$CONTAINER_NAME" 2>/dev/null && docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo "Stopped."
    ;;
  logs)
    docker logs -f "$CONTAINER_NAME"
    ;;
  *)
    echo "Building $IMAGE_NAME..."
    docker build -t "$IMAGE_NAME" .

    docker stop "$CONTAINER_NAME" 2>/dev/null && docker rm "$CONTAINER_NAME" 2>/dev/null || true

    echo "Starting $CONTAINER_NAME..."
    docker run -d \
      --name "$CONTAINER_NAME" \
      -p 8081:8080 \
      -e PORT=8080 \
      ${FIRESTORE_EMULATOR_HOST:+-e FIRESTORE_EMULATOR_HOST="$FIRESTORE_EMULATOR_HOST"} \
      ${GOOGLE_APPLICATION_CREDENTIALS:+-e GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS"} \
      ${GOOGLE_CLOUD_PROJECT:+-e GOOGLE_CLOUD_PROJECT="$GOOGLE_CLOUD_PROJECT"} \
      "$IMAGE_NAME"

    echo "Service running at http://localhost:8081"
    ;;
esac
