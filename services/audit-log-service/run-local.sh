#!/bin/bash
set -e

export ELASTICSEARCH_URL=${ELASTICSEARCH_URL:-"http://localhost:9200"}
export PORT=${PORT:-8080}

cd "$(dirname "$0")"

pip install -r requirements.txt --quiet

python src/app.py
