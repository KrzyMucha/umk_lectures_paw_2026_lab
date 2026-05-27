#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

build_and_run() {
  cd "$ROOT_DIR"
  docker compose up -d --build
  echo "Service running at http://localhost:8084"
  echo "Qdrant dashboard at http://localhost:6333/dashboard"
}

stop_container() {
  cd "$ROOT_DIR"
  docker compose down
  echo "Stopped embedding-service"
}

show_logs() {
  cd "$ROOT_DIR"
  docker compose logs -f app
}

pull_model() {
  cd "$ROOT_DIR"
  echo "Pulling nomic-embed-text model into Ollama..."
  docker exec embedding-service-ollama-1 ollama pull nomic-embed-text
}

seed_data() {
  cd "$ROOT_DIR"
  docker cp scripts/seed.py embedding-service-app-1:/app/seed.py
  docker exec -e QDRANT_URL="http://qdrant:6333" -e OLLAMA_URL="http://ollama:11434" \
    embedding-service-app-1 python /app/seed.py
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
  pull)
    pull_model
    ;;
  seed)
    seed_data
    ;;
  *)
    echo "Usage: ./run-local.sh [stop|logs|seed|pull]"
    exit 1
    ;;
esac
