.PHONY: up down build shell migrate diff cc logs

# Start all containers
up:
	docker compose up -d

# Stop all containers
down:
	docker compose down

# Rebuild images
build:
	docker compose build --no-cache

# Shell into the app container
shell:
	docker compose exec app sh

# Generate a new migration
diff:
	docker compose exec app php bin/console doctrine:migrations:diff

# Run pending migrations
migrate:
	docker compose exec app php bin/console doctrine:migrations:migrate --no-interaction

# Clear Symfony cache
cc:
	docker compose exec app php bin/console cache:clear

# Tail logs
logs:
	docker compose logs -f

# Show registered routes
routes:
	docker compose exec app php bin/console debug:router

# Install / update Composer dependencies
composer-install:
	docker compose exec app composer install

composer-update:
	docker compose exec app composer update
