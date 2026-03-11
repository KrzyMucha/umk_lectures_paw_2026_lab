# ============================================================
# Stage: deps - instalacja zależności composera
# ============================================================
FROM composer:2 AS deps

WORKDIR /app

COPY composer.json composer.lock* ./

# Prod: brak devDependencies, zoptymalizowany autoload
RUN composer install \
    --no-dev \
    --no-scripts \
    --prefer-dist \
    --optimize-autoloader \
    --no-interaction

# ============================================================
# Stage: dev - lokalne środowisko (docker compose)
# ============================================================
FROM php:8.3-cli AS dev

WORKDIR /var/www/html

RUN apt-get update \
    && apt-get install -y --no-install-recommends git unzip libpq-dev \
    && docker-php-ext-install pdo_pgsql \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
COPY docker/php/conf.d/app.ini /usr/local/etc/php/conf.d/app.ini

EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]

# ============================================================
# Stage: prod - obraz produkcyjny dla Cloud Run
# ============================================================
FROM php:8.3-cli AS prod

WORKDIR /var/www/html

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && docker-php-ext-install opcache \
    && rm -rf /var/lib/apt/lists/*

# Optymalne ustawienia PHP dla produkcji
RUN { \
        echo 'opcache.enable=1'; \
        echo 'opcache.memory_consumption=128'; \
        echo 'opcache.validate_timestamps=0'; \
        echo 'expose_php=Off'; \
        echo 'memory_limit=256M'; \
    } > /usr/local/etc/php/conf.d/prod.ini

# Kopiuj zależności z etapu deps
COPY --from=deps /app/vendor ./vendor

# Kopiuj kod aplikacji
COPY . .

# Rozgrzej cache Symfony
RUN APP_ENV=prod php bin/console cache:warmup --no-debug 2>/dev/null || true

# Cloud Run wymaga portu z env PORT (domyślnie 8080)
ENV APP_ENV=prod
EXPOSE 8080

CMD ["sh", "-c", "php -S 0.0.0.0:${PORT:-8080} -t public"]
