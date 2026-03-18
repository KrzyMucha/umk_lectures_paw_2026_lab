#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  deploy_prod_with_rollback.sh \
    --service <cloud-run-service> \
    --region <gcp-region> \
    --image <artifact-registry-image> \
    [--project <gcp-project-id>] \
    [--health-path </health>] \
    [--retries <number>] \
    [--sleep-seconds <number>]

Example:
  ./scripts/deploy_prod_with_rollback.sh \
    --service mini-allegro \
    --region europe-central2 \
    --project project-f5f4f6f0-acae-485b-a16 \
    --image europe-central2-docker.pkg.dev/project-f5f4f6f0-acae-485b-a16/mini-allegro/mini-allegro:latest
EOF
}

SERVICE=""
REGION=""
IMAGE=""
PROJECT=""
HEALTH_PATH="/health"
RETRIES=10
SLEEP_SECONDS=5

while [[ $# -gt 0 ]]; do
  case "$1" in
    --service)
      SERVICE="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --image)
      IMAGE="$2"
      shift 2
      ;;
    --project)
      PROJECT="$2"
      shift 2
      ;;
    --health-path)
      HEALTH_PATH="$2"
      shift 2
      ;;
    --retries)
      RETRIES="$2"
      shift 2
      ;;
    --sleep-seconds)
      SLEEP_SECONDS="$2"
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

if [[ -z "$SERVICE" || -z "$REGION" || -z "$IMAGE" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 1
fi

if [[ -n "$PROJECT" ]]; then
  gcloud config set project "$PROJECT" >/dev/null
fi

echo "Reading current PROD revision before deploy..."
PREVIOUS_REVISION="$(gcloud run services describe "$SERVICE" \
  --region "$REGION" \
  --format='value(status.latestReadyRevisionName)')"

if [[ -z "$PREVIOUS_REVISION" ]]; then
  echo "Cannot determine previous revision for service '$SERVICE'." >&2
  exit 1
fi

echo "Previous revision: $PREVIOUS_REVISION"

echo "Deploying new revision to Cloud Run..."
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --quiet

SERVICE_URL="$(gcloud run services describe "$SERVICE" \
  --region "$REGION" \
  --format='value(status.url)')"
HEALTH_URL="${SERVICE_URL%/}${HEALTH_PATH}"

echo "Running post-deploy healthcheck: $HEALTH_URL"

for ((attempt=1; attempt<=RETRIES; attempt++)); do
  if curl --silent --show-error --fail "$HEALTH_URL" >/dev/null; then
    echo "Healthcheck passed on attempt $attempt/$RETRIES. Deploy kept on new revision."
    exit 0
  fi

  echo "Healthcheck failed ($attempt/$RETRIES). Retrying in ${SLEEP_SECONDS}s..."
  sleep "$SLEEP_SECONDS"
done

echo "Healthcheck failed after $RETRIES attempts. Rolling back traffic to $PREVIOUS_REVISION..." >&2
gcloud run services update-traffic "$SERVICE" \
  --region "$REGION" \
  --to-revisions "${PREVIOUS_REVISION}=100" \
  --quiet

echo "Rollback completed: 100% traffic -> $PREVIOUS_REVISION" >&2
exit 1
