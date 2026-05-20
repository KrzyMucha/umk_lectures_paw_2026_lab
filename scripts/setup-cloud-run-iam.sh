#!/bin/bash

# Quick IAM setup script for Cloud Run services
# Usage: ./scripts/setup-cloud-run-iam.sh

set -e

PROJECT="paw-2026-496213"
REGION="europe-central2"

echo "🔐 Setting up Cloud Run IAM for public access..."
echo ""

# mini-allegro
echo "Setting IAM for mini-allegro..."
gcloud run services add-iam-policy-binding mini-allegro \
  --region=$REGION \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=$PROJECT \
  --quiet

echo "✓ mini-allegro now publicly accessible"
echo ""

# purchase-service-dev
echo "Setting IAM for purchase-service-dev..."
gcloud run services add-iam-policy-binding purchase-service-dev \
  --region=$REGION \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=$PROJECT \
  --quiet

echo "✓ purchase-service-dev now publicly accessible"
echo ""

echo "✅ Cloud Run services are now public!"
echo ""
echo "Testing access..."

# Test mini-allegro
MINI_URL=$(gcloud run services describe mini-allegro \
  --region=$REGION \
  --project=$PROJECT \
  --format='value(status.url)')

echo "mini-allegro: $MINI_URL"
curl -s -o /dev/null -w "HTTP %{http_code}" "$MINI_URL/health" || echo "HTTP error"
echo ""

# Test purchase-service
PURCHASE_URL=$(gcloud run services describe purchase-service-dev \
  --region=$REGION \
  --project=$PROJECT \
  --format='value(status.url)')

echo "purchase-service: $PURCHASE_URL"
curl -s -o /dev/null -w "HTTP %{http_code}" "$PURCHASE_URL/health" || echo "HTTP error"
echo ""

echo "✅ All set! Services are publicly accessible."
