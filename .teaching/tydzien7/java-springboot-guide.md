# Przewodnik: serwis w Java + Spring Boot

Instrukcje krok po kroku do wydzielenia encji z monolitu Symfony do serwisu w Java Spring Boot.
Każdy krok zawiera gotowy prompt do wklejenia w Copilot/asystenta AI.

Wszędzie gdzie widzisz `[ENCJA]` / `[encja]` / `[endpoint]` — podstaw swoją encję (np. `Offer` / `offer` / `offers`).

---

## Wymagania

- Java 21+ (sprawdź: `java --version`)
- Docker
- Dostęp do Cloud SQL (Cloud SQL Proxy)

Jeśli nie masz Javy lokalnie — nie szkodzi, wszystko budujemy w Dockerze.

---

## Krok 1a — Wygeneruj projekt Spring Boot

Wklej do Copilota:

> Stwórz projekt Spring Boot w katalogu `services/[encja]-service/`.
>
> Wymagania:
> - Java 21, Gradle (Kotlin DSL — `build.gradle.kts`)
> - Spring Boot 3.3+
> - Zależności: `spring-boot-starter-web`, `spring-boot-starter-jdbc`
> - Sterownik: `org.postgresql:postgresql`
> - Struktura katalogów:
>
> ```
> services/[encja]-service/
> ├── build.gradle.kts
> ├── settings.gradle.kts
> ├── Dockerfile
> ├── src/main/java/com/paw/[encja]/
> │   ├── Application.java
> │   ├── [Encja]Controller.java
> │   └── [Encja].java
> └── src/main/resources/
>     └── application.properties
> ```
>
> W `application.properties`:
> ```
> server.port=${PORT:8080}
> ```
>
> Serwis powinien nasłuchiwać na porcie z zmiennej środowiskowej `PORT` (domyślnie 8080).
> Na razie **bez bazy danych** — to dodamy później.

**Checkpoint:** Masz katalog z `build.gradle.kts`, `Application.java` i `application.properties`.

---

## Krok 1b — Endpoint z hardkodowanymi danymi

Wklej do Copilota:

> W projekcie Spring Boot w `services/[encja]-service/` stwórz:
>
> 1. Klasę `[Encja].java` — POJO z polami identycznymi jak w odpowiedzi monolitu.
>    Aktualny format JSON z monolitu:
>    ```json
>    [wklej output z: curl -s http://localhost:8080/[endpoint] | python3 -m json.tool]
>    ```
>
> 2. Klasę `[Encja]Controller.java` z:
>    - `GET /[endpoint]` — zwraca `List<[Encja]>` z 3 hardkodowanymi rekordami
>    - `GET /[endpoint]/{id}` — zwraca pojedynczy rekord po ID (lub 404)
>
> Format JSON odpowiedzi musi być **identyczny** z monolitem — te same nazwy pól, te same typy.
> Użyj `@RestController` i `@RequestMapping("/[endpoint]")`.

**Checkpoint:** Masz `[Encja]Controller.java` z hardkodowanymi danymi.

---

## Krok 1c — Dockerfile

Wklej do Copilota:

> Stwórz `Dockerfile` w `services/[encja]-service/` dla projektu Spring Boot z Gradle.
>
> Wymagania:
> - Multi-stage build
> - Stage 1 (`builder`): `eclipse-temurin:21-jdk-alpine`, kopiuj źródła, uruchom `./gradlew bootJar`
> - Stage 2 (`runtime`): `eclipse-temurin:21-jre-alpine`, kopiuj JAR z buildera
> - Entrypoint: `java -jar app.jar`
> - Nie kopiuj `.gradle/` ani `build/` — dodaj `.dockerignore`
>
> Stwórz też `.dockerignore`:
> ```
> .gradle/
> build/
> .idea/
> *.iml
> ```

Gotowy Dockerfile dla odniesienia (jeśli Copilot wygeneruje coś dziwnego):

```dockerfile
# Stage 1: Build
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY gradle/ gradle/
COPY gradlew build.gradle.kts settings.gradle.kts ./
RUN ./gradlew dependencies --no-daemon || true
COPY src/ src/
RUN ./gradlew bootJar --no-daemon

# Stage 2: Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Checkpoint:** `Dockerfile` i `.dockerignore` istnieją.

---

## Krok 1d — Skrypt `run-local.sh`

Wklej do Copilota:

> Stwórz skrypt `services/[encja]-service/run-local.sh` (bash):
>
> ```bash
> #!/bin/bash
> set -e
>
> SERVICE_NAME="[encja]-service"
> PORT=8081
>
> case "${1:-start}" in
>   start)
>     echo "Building $SERVICE_NAME..."
>     docker build -t $SERVICE_NAME .
>     docker rm -f $SERVICE_NAME 2>/dev/null || true
>     echo "Starting $SERVICE_NAME on port $PORT..."
>     docker run -d --name $SERVICE_NAME \
>       -p $PORT:8080 \
>       -e PORT=8080 \
>       ${DATABASE_URL:+-e DATABASE_URL="$DATABASE_URL"} \
>       $SERVICE_NAME
>     echo "Service running at http://localhost:$PORT"
>     ;;
>   stop)
>     docker rm -f $SERVICE_NAME
>     ;;
>   logs)
>     docker logs -f $SERVICE_NAME
>     ;;
>   *)
>     echo "Usage: $0 {start|stop|logs}"
>     ;;
> esac
> ```
>
> Zwróć uwagę: `${DATABASE_URL:+-e DATABASE_URL="$DATABASE_URL"}` — przekazuje zmienną
> tylko jeśli jest ustawiona. Na razie nie mamy bazy, więc serwis startuje bez niej.

Uruchom:

```bash
cd services/[encja]-service
chmod +x run-local.sh
./run-local.sh
```

Sprawdź:

```bash
curl -s http://localhost:8081/[endpoint] | python3 -m json.tool
```

**Checkpoint:** Serwis zwraca hardkodowane dane na `localhost:8081`.

---

## Krok 1e — Health check endpoint

Cloud Run sprawdza czy serwis żyje robiąc `GET /`. Jeśli zwróci 404, Cloud Run uzna serwis za niezdrowy.

Wklej do Copilota:

> Dodaj w Spring Boot endpoint health check:
> - `GET /` — zwraca `{"status": "ok", "service": "[encja]-service"}` z HTTP 200
>
> Może to być osobny `HealthController` albo dodatkowa metoda w istniejącym kontrolerze.

Sprawdź:

```bash
curl -s http://localhost:8081/ | python3 -m json.tool
```

**Checkpoint:** `GET /` zwraca 200.

---

## Krok 2 — Deploy (Terraform + CI/CD)

Tutaj wracasz do głównego zadania (`zadanie_7_1.md`, Krok 2). Prompty dla Terraform i CI/CD są generyczne — działają niezależnie od technologii.

Jedyna uwaga Java-specyficzna: **pierwszy cold start na Cloud Run może trwać 5-10 sekund** (JVM startup). To normalne. Jeśli chcesz przyspieszyć, dodaj do `Dockerfile`:

```dockerfile
ENTRYPOINT ["java", "-XX:+UseSerialGC", "-Xss512k", "-Xmx256m", "-jar", "app.jar"]
```

To ogranicza zużycie pamięci i przyspiesza start (kosztem throughputu — ale do labów wystarczy).

---

## Krok 3a — Podłączenie do bazy (lokalnie)

Wklej do Copilota:

> W projekcie Spring Boot w `services/[encja]-service/` chcę podłączyć się do PostgreSQL.
>
> Mam już zależności `spring-boot-starter-jdbc` i `postgresql` w `build.gradle.kts`.
>
> 1. W `application.properties` skonfiguruj datasource przez zmienną `DATABASE_URL`:
>    ```properties
>    spring.datasource.url=${DATABASE_URL:}
>    ```
>    Spring Boot powinien parsować standardowy format `postgresql://user:pass@host:port/dbname`.
>    Jeśli Spring nie parsuje tego formatu, użyj osobnych zmiennych:
>    ```properties
>    spring.datasource.url=jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:paw}
>    spring.datasource.username=${DB_USER:postgres}
>    spring.datasource.password=${DB_PASSWORD:}
>    ```
>
> 2. Stwórz klasę `[Encja]Repository.java` która używa `JdbcTemplate`:
>    - metoda `findAll()` — `SELECT * FROM [tabela]`, mapuje wiersze na `[Encja]`
>    - metoda `findById(int id)` — `SELECT * FROM [tabela] WHERE id = ?`
>
> 3. Zmień `[Encja]Controller` — wstrzyknij `[Encja]Repository` i użyj go zamiast hardkodowanych danych.
>    Jeśli `DATABASE_URL` nie jest ustawiony — niech serwis startuje, ale `GET /[endpoint]` zwraca 503
>    z komunikatem "Database not configured".
>
> Schemat tabeli (skopiuj z migracji monolitu lub uruchom):
> ```
> [wklej output z: psql $DATABASE_URL -c "\d [tabela]"]
> ```
>
> Nie twórz migracji — tabela już istnieje (stworzona przez monolit).

Uwaga: Spring Boot standardowo oczekuje `jdbc:postgresql://` a nie `postgresql://`. Są dwa podejścia:

**Podejście A** — osobne zmienne (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`):
```bash
DATABASE_URL nie jest używany, zamiast tego:
DB_HOST=host.docker.internal DB_PORT=5433 DB_NAME=paw DB_USER=postgres DB_PASSWORD=haslo ./run-local.sh
```

**Podejście B** — parsowanie `DATABASE_URL` w kodzie (klasa `@Configuration` która rozbija URL na części).

Wybierz to co wygodniej — oba są OK. Ważne żeby na Cloud Run działało z tymi samymi zmiennymi co monolit.

Uruchom Cloud SQL Proxy i serwis:

```bash
# Terminal 1: proxy
cloud-sql-proxy PROJECT_ID:europe-central2:INSTANCE_NAME --port=5433

# Terminal 2: serwis
cd services/[encja]-service
DB_HOST=host.docker.internal DB_PORT=5433 DB_NAME=paw-dev DB_USER=postgres DB_PASSWORD=haslo ./run-local.sh
```

Sprawdź:

```bash
curl -s http://localhost:8081/[endpoint] | python3 -m json.tool
```

**Checkpoint:** Dane z bazy, identyczne z monolitem.

---

## Krok 3b — Cloud SQL na Cloud Run

Wklej do Copilota:

> Mam Spring Boot service deployowany na Cloud Run.
> Monolit Symfony łączy się z Cloud SQL przez Unix socket (Cloud SQL Auth Proxy wbudowany w Cloud Run).
>
> Dla Spring Boot na Cloud Run potrzebuję:
> 1. W Terraform: dodaj Cloud SQL instance connection w konfiguracji Cloud Run
>    (annotation `run.googleapis.com/cloudsql-instances` lub blok `cloud_sql_instance` w template)
> 2. Spring Boot łączy się do Cloud SQL przez socket. JDBC URL wygląda tak:
>    ```
>    jdbc:postgresql:///DB_NAME?cloudSqlInstance=PROJECT:REGION:INSTANCE&socketFactory=com.google.cloud.sql.postgres.SocketFactory
>    ```
> 3. Dodaj zależność w `build.gradle.kts`:
>    ```kotlin
>    implementation("com.google.cloud.sql:postgres-socket-factory:1.15.0")
>    ```
>
> Moja konfiguracja Terraform monolitu (wklej):
> [wklej konfigurację Cloud Run monolitu z pliku .tf]
>
> Hasło do bazy jest w Secret Manager pod nazwą: [wklej nazwę sekretu]

Ważne: `postgres-socket-factory` to biblioteka Google która pozwala Spring Boot łączyć się z Cloud SQL przez socket zamiast TCP. Bez niej — connection refused.

Push, merge, sprawdź:

```bash
curl -s https://[SERVICE_URL]/[endpoint] | python3 -m json.tool
```

**Checkpoint:** Serwis na Cloud Run zwraca dane z Cloud SQL.

---

## Krok 4 — Podmiana

Wróć do głównego zadania (`zadanie_7_1.md`, Krok 4). Prompty są generyczne — dotyczą monolitu Symfony, nie nowego serwisu.

---

## Troubleshooting

### `./gradlew: Permission denied` w Dockerze

Dodaj na początku Dockerfile:
```dockerfile
RUN chmod +x gradlew
```

### Build trwa bardzo długo (~5-10 min za pierwszym razem)

To normalne — Gradle pobiera zależności. Kolejne buildy będą szybsze dzięki cache warstw Dockera. Upewnij się że w Dockerfile **najpierw** kopiujesz `build.gradle.kts` i uruchamiasz `./gradlew dependencies`, a **potem** kopiujesz `src/`. Dzięki temu zmiana kodu nie invaliduje cache zależności.

### Spring Boot nie parsuje `DATABASE_URL` w formacie `postgresql://`

Spring Boot oczekuje `jdbc:postgresql://`. Rozwiązanie: użyj osobnych zmiennych (`DB_HOST`, `DB_PORT`, itd.) lub napisz `@Configuration` class który parsuje URL.

### `Connection refused` na Cloud Run

- Sprawdź czy `postgres-socket-factory` jest w zależnościach
- Sprawdź czy Cloud SQL instance connection jest w konfiguracji Cloud Run (Terraform)
- Sprawdź czy service account ma `roles/cloudsql.client`

### Cold start trwa >10 sekund

Dodaj flagi JVM w Dockerfile:
```dockerfile
ENTRYPOINT ["java", "-XX:+UseSerialGC", "-Xss512k", "-Xmx256m", "-jar", "app.jar"]
```

Alternatywa: użyj GraalVM Native Image (zaawansowane — nie na tych zajęciach).

### `Whitelabel Error Page` na `GET /`

Brakuje health check endpointu. Dodaj kontroler zwracający 200 na `/`.
