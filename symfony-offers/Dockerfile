FROM php:8.3-cli-alpine AS base

RUN apk add --no-cache \
    bash \
    git \
    unzip \
    libpq-dev \
    && docker-php-ext-install pdo pdo_pgsql

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

# ── Development ──────────────────────────────────────────────────────────────
FROM base AS dev

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["docker-entrypoint.sh"]

# ── Production ───────────────────────────────────────────────────────────────
FROM base AS prod

COPY . .

RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress \
    && php bin/console cache:warmup --env=prod

EXPOSE 8080
CMD ["php", "-S", "0.0.0.0:8080", "-t", "public"]
