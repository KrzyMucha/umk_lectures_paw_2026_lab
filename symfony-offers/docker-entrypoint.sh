#!/bin/bash
set -e

echo "==> Installing/updating dependencies..."
composer install --no-interaction --optimize-autoloader --no-progress

echo "==> Starting PHP built-in server on 0.0.0.0:8080..."
exec php -S 0.0.0.0:8080 -t public
