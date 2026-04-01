#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PROJECT_ID="project-f5f4f6f0-acae-485b-a16"
REGION="europe-central2"
REPOSITORY="mini-allegro"
IMAGE_NAME="mini-allegro"
SERVICE_NAME="mini-allegro-dev"
BUILD_CONTEXT="$ROOT_DIR/services/symphony-monolith"
DOCKERFILE="$ROOT_DIR/services/symphony-monolith/docker/Dockerfile"
REMOVE_SERVER_VERSION="false"
RUN_PRODUCTS_CHECK="true"
PLATFORM="linux/amd64"
# DEV-only fallback – w CI/CD ustaw APP_SECRET jako secret w GitHub/Cloud Build
APP_SECRET="${APP_SECRET:-de7af9309aaba9542fe4fe4de71c4f82}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/quick-dev-loop.sh [options]

Description:
  Fast manual DEV loop for Cloud Run:
  1) Resolve DATABASE_URL (from env or terraform output)
  2) Build prod image
  3) Push image to Artifact Registry
  4) Deploy Cloud Run service with APP_ENV=dev and DATABASE_URL
  5) Check /health (and optionally /products)

Options:
  --project-id <id>         GCP project id (default: project-f5f4f6f0-acae-485b-a16)
  --region <region>         Cloud Run/Artifact Registry region (default: europe-central2)
  --service <name>          Cloud Run service name (default: mini-allegro-dev)
  --repository <name>       Artifact Registry repository (default: mini-allegro)
  --image-name <name>       Image name (default: mini-allegro)
  --tag <tag>               Image tag (default: manual-<timestamp>-<gitsha>)
  --database-url <url>      Override DATABASE_URL directly
  --platform <platform>     Build platform for Cloud Run image (default: linux/amd64)
  --keep-server-version     Do not strip serverVersion query param from DATABASE_URL
  --skip-products-check     Check only /health
  --app-secret <secret>     Override APP_SECRET (default: DEV hardcoded fallback)
  -h, --help                Show this help

Examples:
  ./scripts/quick-dev-loop.sh
  ./scripts/quick-dev-loop.sh --service mini-allegro-dev-debug --skip-products-check
  ./scripts/quick-dev-loop.sh --database-url 'postgresql://app:pass@1.2.3.4:5432/mini_allegro_dev'
EOF
}

ensure_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

resolve_database_url() {
  if [[ -n "${DATABASE_URL_OVERRIDE:-}" ]]; then
    DATABASE_URL="$DATABASE_URL_OVERRIDE"
    return
  fi

  if [[ -n "${DATABASE_URL:-}" ]]; then
    return
  fi

  if ! command -v terraform >/dev/null 2>&1; then
    echo "DATABASE_URL is not set and terraform is unavailable." >&2
    echo "Set DATABASE_URL in env or pass --database-url." >&2
    exit 1
  fi

  local tf_url
  tf_url="$(terraform -chdir="$ROOT_DIR/infra/dev" output -raw database_url 2>/dev/null || true)"

  if [[ -z "$tf_url" ]]; then
    echo "Cannot resolve infra/dev output database_url." >&2
    echo "Run terraform apply in infra/dev or pass --database-url." >&2
    exit 1
  fi

  DATABASE_URL="$tf_url"
}

sanitize_database_url() {
  if [[ "$REMOVE_SERVER_VERSION" == "true" ]]; then
    DATABASE_URL="$(printf '%s' "$DATABASE_URL" | sed -E 's/[?&]serverVersion=[^&]*//g; s/[?&]$//; s/\?&/\?/g')"
  fi
}

TAG="manual-$(date +%s)-$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo nogit)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-id)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --service)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --repository)
      REPOSITORY="$2"
      shift 2
      ;;
    --image-name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --database-url)
      DATABASE_URL_OVERRIDE="$2"
      shift 2
      ;;
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --keep-server-version)
      REMOVE_SERVER_VERSION="false"
      shift
      ;;
    --skip-products-check)
      RUN_PRODUCTS_CHECK="false"
      shift
      ;;
    --app-secret)
      APP_SECRET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

ensure_cmd gcloud
ensure_cmd docker
ensure_cmd curl

if ! docker buildx version >/dev/null 2>&1; then
  echo "docker buildx is required (missing in current Docker installation)." >&2
  exit 1
fi

if [[ ! -f "$DOCKERFILE" ]]; then
  echo "Dockerfile not found: $DOCKERFILE" >&2
  exit 1
fi

resolve_database_url
sanitize_database_url

if [[ -z "$DATABASE_URL" ]]; then
  echo "Resolved DATABASE_URL is empty." >&2
  exit 1
fi

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}"

echo "==> Configuring docker auth for Artifact Registry"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo "==> Building and pushing image for platform $PLATFORM: $IMAGE"
docker buildx build \
  --platform "$PLATFORM" \
  --target prod \
  -f "$DOCKERFILE" \
  -t "$IMAGE" \
  --push \
  "$BUILD_CONTEXT"

echo "==> Deploying Cloud Run service: $SERVICE_NAME"
gcloud run deploy "$SERVICE_NAME" \
  --region "$REGION" \
  --image "$IMAGE" \
  --set-env-vars "APP_ENV=dev,DATABASE_URL=$DATABASE_URL,APP_SECRET=$APP_SECRET" \
  --quiet

URL="$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)')"

if [[ -z "$URL" ]]; then
  echo "Could not resolve service URL for $SERVICE_NAME" >&2
  exit 1
fi

echo "==> Service URL: $URL"

echo "==> Checking /health"
curl -fsS -i "$URL/health" | head -n 30

if [[ "$RUN_PRODUCTS_CHECK" == "true" ]]; then
  echo "==> Checking /products"
  curl -fsS -i "$URL/products" | head -n 40
fi

echo "==> Done"
echo "Image: $IMAGE"
echo "URL:   $URL"
