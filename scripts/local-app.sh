#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/symphony-monolith"
DOCKER_DIR="$SERVICE_DIR/docker"
COMPOSE_FILES=(
  -f "$DOCKER_DIR/docker-compose.yml"
  -f "$DOCKER_DIR/compose.override.yaml"
)

usage() {
  cat <<'EOF'
Usage:
  ./scripts/local-app.sh <command>

Commands:
  up         Build, start and stream app logs (Ctrl+C stops app)
  down       Stop stack and remove volumes
  restart    Recreate app container and stream logs (Ctrl+C stops app)
  logs       Show docker compose logs (follow mode)
  status     Show docker compose services status
  test       Run Python integration tests (integ-tests)
  help       Show this help

Examples:
  ./scripts/local-app.sh up
  ./scripts/local-app.sh logs
  ./scripts/local-app.sh test
EOF
}

run_compose() {
  docker compose "${COMPOSE_FILES[@]}" "$@"
}

ensure_paths() {
  if [[ ! -d "$SERVICE_DIR" ]]; then
    echo "Service directory not found: $SERVICE_DIR" >&2
    exit 1
  fi

  if [[ ! -f "$DOCKER_DIR/docker-compose.yml" ]]; then
    echo "docker-compose.yml not found in: $DOCKER_DIR" >&2
    exit 1
  fi
}

<<<<<<< HEAD
=======
ensure_port_free() {
  local port="${1:-8080}"

  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $port is already in use. Cannot start app." >&2
    echo >&2
    echo "Listening processes on port $port:" >&2
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >&2 || true
    echo >&2

    local docker_using_port
    docker_using_port="$(docker ps --filter publish="$port" --format 'table {{.ID}}\t{{.Names}}\t{{.Ports}}')"
    if [[ "$(echo "$docker_using_port" | wc -l | tr -d ' ')" -gt 1 ]]; then
      echo "Docker containers publishing port $port:" >&2
      echo "$docker_using_port" >&2
      echo >&2
    fi

    echo "Free the port and try again (example: docker stop <container_id> or kill <pid>)." >&2
    exit 1
  fi
}

>>>>>>> dca59cf (refactoring - running scripts)
cmd="${1:-help}"

ensure_paths

case "$cmd" in
  up)
<<<<<<< HEAD
=======
    ensure_port_free 8080
>>>>>>> dca59cf (refactoring - running scripts)
    run_compose up --build --no-deps app
    ;;
  down)
    run_compose down -v
    ;;
  restart)
    run_compose down -v
<<<<<<< HEAD
=======
    ensure_port_free 8080
>>>>>>> dca59cf (refactoring - running scripts)
    run_compose up --build --no-deps app
    ;;
  logs)
    run_compose logs -f app
    ;;
  status)
    run_compose ps app
    ;;
  test)
    VENV_DIR="$ROOT_DIR/.venv"
    PY_REQ="$SERVICE_DIR/requirements-dev.txt"

    if [[ ! -d "$VENV_DIR" ]]; then
      python3 -m venv "$VENV_DIR"
    fi

    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    pip install -r "$PY_REQ"
    APP_BASE_URL="${APP_BASE_URL:-http://localhost:8080}" pytest "$ROOT_DIR/integ-tests"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac
