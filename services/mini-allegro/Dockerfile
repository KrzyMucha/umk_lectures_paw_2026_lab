# syntax=docker/dockerfile:1
FROM dunglas/frankenphp:php8.3-alpine AS base

RUN install-php-extensions pdo_pgsql opcache intl zip

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app

# --- dev stage ---
FROM base AS dev

ENV APP_ENV=dev

CMD ["php", "-S", "0.0.0.0:8080", "-t", "public"]

# --- prod stage ---
FROM base AS prod

ENV APP_ENV=prod

RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" && \
    echo "opcache.enable=1\nopcache.memory_consumption=128\nopcache.max_accelerated_files=10000" \
    >> "$PHP_INI_DIR/conf.d/opcache.ini"

COPY composer.json composer.lock* ./
RUN --mount=type=cache,target=/root/.composer/cache \
    composer install --no-dev --no-scripts --no-autoloader

COPY . .

RUN --mount=type=cache,target=/root/.composer/cache \
    composer dump-autoload --optimize --classmap-authoritative && \
    php bin/console cache:warmup

EXPOSE 8080

CMD ["php", "-S", "0.0.0.0:8080", "-t", "public"]
