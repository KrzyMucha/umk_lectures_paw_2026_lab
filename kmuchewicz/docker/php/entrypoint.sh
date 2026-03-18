#!/bin/sh
set -e

export COMPOSER_ALLOW_SUPERUSER=1

echo "Installing Composer dependencies..."
composer install --no-interaction --prefer-dist

echo "Waiting for database..."
until php -r "new PDO('pgsql:host=database;dbname=app', 'app', 'secret');" 2>/dev/null; do
    sleep 1
done

echo "Running migrations..."
php bin/console doctrine:migrations:migrate --no-interaction --allow-no-migration

echo "Starting PHP-FPM..."
exec "$@"
