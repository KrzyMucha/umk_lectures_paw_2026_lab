#!/bin/bash

# GCP Migration Automation Script - May 2026
# Usage: ./gcp-migration.sh [apply-iam|migrate-db|deploy-product-review|run-tests|all]

set -e

# ============ CONFIG ============
PROJECT="paw-2026-496213"
REGION="europe-central2"
INFRA_DIR="./infra"
SERVICES_DIR="./services"
INTEG_TESTS_DIR="./integ-tests"

DB_DEV_INSTANCE="mini-allegro-db-dev"
DB_DEV_NAME="mini_allegro_dev"
DB_PROD_INSTANCE="mini-allegro-db-prod"
DB_PROD_NAME="mini_allegro_prod"
DB_USER="app"

# ============ COLORS ============
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============ FUNCTIONS ============

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
  exit 1
}

log_warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

# ============ 1. Apply IAM ============

apply_iam() {
  log_warning "Cloud Run IAM setup requires run.services.setIamPolicy permission"
  log_info "This account does not have this permission - using manual gcloud commands instead"

  cd "$INFRA_DIR"
  
  log_info "Running terraform init (for other resources)..."
  terraform init -upgrade 2>&1 | grep -E "Terraform|Successfully|already" || true

  log_info "To enable public access to Cloud Run services, run these commands:"
  echo ""
  echo "gcloud run services add-iam-policy-binding mini-allegro \\"
  echo "  --region=europe-central2 \\"
  echo "  --member=allUsers \\"
  echo "  --role=roles/run.invoker \\"
  echo "  --project=paw-2026-496213"
  echo ""
  echo "gcloud run services add-iam-policy-binding purchase-service-dev \\"
  echo "  --region=europe-central2 \\"
  echo "  --member=allUsers \\"
  echo "  --role=roles/run.invoker \\"
  echo "  --project=paw-2026-496213"
  echo ""
  
  log_success "Copy & paste the commands above to set IAM manually"
  
  cd - > /dev/null
}

# ============ 2. Migrate Database ============

migrate_db() {
  local env=${1:-dev}
  
  if [[ "$env" != "dev" && "$env" != "prod" ]]; then
    log_error "Invalid environment: $env. Use 'dev' or 'prod'."
  fi

  log_info "Starting DB migration for $env environment..."

  if [[ "$env" == "dev" ]]; then
    INSTANCE=$DB_DEV_INSTANCE
    DB_NAME=$DB_DEV_NAME
  else
    INSTANCE=$DB_PROD_INSTANCE
    DB_NAME=$DB_PROD_NAME
  fi

  log_info "Fetching DB password from Terraform state..."
  cd "$INFRA_DIR"
  if [[ "$env" == "dev" ]]; then
    DB_PASSWORD=$(terraform output -json 2>/dev/null | jq -r '.dev_db_password.value' 2>/dev/null || echo "")
  else
    DB_PASSWORD=$(terraform output -json 2>/dev/null | jq -r '.prod_db_password.value' 2>/dev/null || echo "")
  fi
  cd - > /dev/null

  if [[ -z "$DB_PASSWORD" ]]; then
    log_error "Could not fetch DB password. Check Terraform state."
  fi

  log_info "Fetching Cloud SQL IP..."
  DB_IP=$(gcloud sql instances describe "$INSTANCE" \
    --project="$PROJECT" \
    --format='value(ipAddresses[0].ipAddress)' 2>/dev/null)

  if [[ -z "$DB_IP" ]]; then
    log_error "Could not fetch Cloud SQL IP for $INSTANCE"
  fi

  log_success "DB IP: $DB_IP"

  log_info "Building mini-allegro image..."
  IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/mini-allegro:latest"
  
  # Sprawdź czy image istnieje w Artifact Registry
  if ! gcloud artifacts docker images list "${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro" --project="$PROJECT" --quiet 2>/dev/null | grep -q "mini-allegro"; then
    log_warning "Image not found in Artifact Registry, building locally..."
    cd "$SERVICES_DIR/symphony-monolith"
    docker build -t "$IMAGE" .
    gcloud auth configure-docker "${REGION}-docker.pkg.dev"
    docker push "$IMAGE"
    cd - > /dev/null
  fi

  log_info "Running Doctrine migrations..."
  docker run --rm \
    -e "DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_IP}:5432/${DB_NAME}?sslmode=require" \
    -e "APP_ENV=prod" \
    "$IMAGE" \
    php bin/console doctrine:migrations:migrate --no-interaction

  log_success "Database migrations completed for $env"
}

# ============ 3. Deploy product-review-service ============

deploy_product_review() {
  log_info "Building and deploying product-review-service..."

  SERVICE_NAME="product-review-service-dev"
  IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/mini-allegro/${SERVICE_NAME}:latest"

  log_info "Authenticating with Artifact Registry..."
  gcloud auth configure-docker "${REGION}-docker.pkg.dev"

  log_info "Building Docker image..."
  cd "$SERVICES_DIR/product-review-service"
  docker build -t "$IMAGE" .

  log_info "Pushing image to Artifact Registry..."
  docker push "$IMAGE"
  cd - > /dev/null

  log_info "Deploying to Cloud Run..."
  gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE" \
    --region="$REGION" \
    --project="$PROJECT" \
    --memory=512Mi \
    --cpu=1 \
    --port=8080 \
    --allow-unauthenticated \
    --no-traffic \
    --quiet

  SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT" \
    --format='value(status.url)')

  log_success "product-review-service deployed at: $SERVICE_URL"
  
  log_info "Add this URL to mini-allegro env var in infra/main.tf:"
  echo "  PRODUCT_REVIEW_SERVICE_URL=$SERVICE_URL"
}

# ============ 4. Run Integration Tests ============

run_tests() {
  log_info "Setting up test environment..."

  # Fetch service URLs
  MINI_ALLEGRO_URL=$(gcloud run services describe "mini-allegro" \
    --region="$REGION" \
    --project="$PROJECT" \
    --format='value(status.url)' 2>/dev/null || echo "http://localhost:8000")

  PURCHASE_SERVICE_URL=$(gcloud run services describe "purchase-service-dev" \
    --region="$REGION" \
    --project="$PROJECT" \
    --format='value(status.url)' 2>/dev/null || echo "http://localhost:8001")

  PRODUCT_REVIEW_SERVICE_URL=$(gcloud run services describe "product-review-service-dev" \
    --region="$REGION" \
    --project="$PROJECT" \
    --format='value(status.url)' 2>/dev/null || echo "http://localhost:8002")

  log_info "Test URLs:"
  echo "  mini-allegro: $MINI_ALLEGRO_URL"
  echo "  purchase-service: $PURCHASE_SERVICE_URL"
  echo "  product-review-service: $PRODUCT_REVIEW_SERVICE_URL"

  log_info "Installing test dependencies..."
  pip install -q -r "$INTEG_TESTS_DIR/requirements.txt" || log_warning "Some packages failed to install"

  log_info "Running integration tests..."
  cd "$INTEG_TESTS_DIR"
  
  export MINI_ALLEGRO_URL
  export PURCHASE_SERVICE_URL
  export PRODUCT_REVIEW_SERVICE_URL

  pytest . -v --tb=short

  log_success "Tests completed"
  cd - > /dev/null
}

# ============ 6. Check Prerequisites ============

check_prereqs() {
  log_info "Checking prerequisites..."

  local missing=0

  if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI not found. Install Google Cloud SDK."
    ((missing++))
  fi

  if ! command -v terraform &> /dev/null; then
    log_error "terraform not found. Install Terraform."
    ((missing++))
  fi

  if ! command -v docker &> /dev/null; then
    log_error "docker not found. Install Docker."
    ((missing++))
  fi

  if [[ $missing -gt 0 ]]; then
    log_error "$missing prerequisite(s) missing"
  fi

  log_info "Checking gcloud authentication..."
  if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    log_error "Not authenticated with gcloud. Run: gcloud auth login"
  fi

  log_success "All prerequisites met"
}

# ============ MAIN ============

main() {
  local action=${1:-all}

  check_prereqs

  case "$action" in
    apply-iam)
      apply_iam
      ;;
    migrate-db)
      migrate_db "${2:-dev}"
      ;;
    deploy-product-review)
      deploy_product_review
      ;;
    run-tests)
      run_tests
      ;;
    all)
      log_info "Running full migration pipeline..."
      apply_iam
      migrate_db dev
      deploy_product_review
      run_tests
      log_success "✅ Full migration completed!"
      ;;
    *)
      echo "Usage: $0 [apply-iam|migrate-db|deploy-product-review|run-tests|all]"
      echo ""
      echo "Examples:"
      echo "  $0 apply-iam                    # Apply Terraform IAM rules"
      echo "  $0 migrate-db dev               # Run DB migrations for DEV"
      echo "  $0 migrate-db prod              # Run DB migrations for PROD"
      echo "  $0 deploy-product-review        # Build & deploy product-review-service"
      echo "  $0 run-tests                    # Run integration tests"
      echo "  $0 all                          # Run all steps"
      exit 1
      ;;
  esac
}

main "$@"
