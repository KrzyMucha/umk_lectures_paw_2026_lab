# Zadanie 7.1: Wydzielenie serwisu z monolitu

Wydzielasz encję którą podłączyłeś do bazy (Offer, User lub Purchase) do **osobnego serwisu** w wybranej technologii. Serwis zastąpi odpowiednią część monolitu Symfony.

Pracujesz **krok po kroku**. Każdy krok kończy się działającym checkpointem — nie przechodź dalej zanim nie działa.

---

## Zanim zaczniesz

### Wybierz technologię

Napisz nowy serwis w jednym z tych języków:

| Technologia | Framework / narzędzie | Uwagi |
|-------------|----------------------|-------|
| Java | Spring Boot | Solidny wybór, ogromny ekosystem |
| Kotlin | Spring Boot / Ktor | Na JVM, dostęp do ekosystemu Javy |
| Python | FastAPI / Flask | Szybkie prototypowanie, dobry support GCP |
| Go | net/http / Gin / Echo | Prosty, szybka kompilacja, cloud-native |
| Rust | actix-web / axum | Wydajny, ale trudniejsza krzywa uczenia |

Pamiętaj: serwis musi się integrować z GCP (Cloud Run, Cloud SQL). Sprawdź czy Twój język ma:
- Sterownik PostgreSQL
- Dockerfile który działa na Cloud Run
- SDK/bibliotekę do logowania (stdout JSON wystarczy)

### Utwórz branch

```bash
git checkout develop
git pull origin develop
git checkout -b feat/[encja]-service
```

### Struktura katalogów

Nowy serwis tworzysz obok monolitu:

```
services/
├── symphony-monolith/     ← istniejący monolit
└── [encja]-service/       ← Twój nowy serwis
    ├── src/               ← kod źródłowy
    ├── Dockerfile
    ├── run-local.sh       ← skrypt do uruchomienia lokalnie
    └── README.md
```

---

## Krok 1 — Szkielet serwisu z hardkodowanymi danymi

Stwórz minimalny serwis HTTP który zwraca hardkodowane dane na endpoincie Twojej encji.

Wklej do asystenta:

> Tworzę nowy serwis w [TECHNOLOGIA] ([FRAMEWORK]).
> Serwis ma wystawić endpoint REST:
> - `GET /[endpoint]` — zwraca listę [ENCJA] jako JSON
> - `GET /[endpoint]/{id}` — zwraca pojedynczą [ENCJA] po ID
>
> Na razie zwracaj **hardkodowane dane** (3-4 przykładowe rekordy).
> Format JSON musi być identyczny z tym co zwraca monolit Symfony na tym samym endpoincie.
>
> Aktualny format odpowiedzi z monolitu (skopiuj output):
> [wklej output z `curl -s http://localhost:8080/[endpoint] | python3 -m json.tool`]
>
> Stwórz strukturę projektu w katalogu `services/[encja]-service/`.
> Dodaj `Dockerfile` (multi-stage build, obraz wynikowy jak najlżejszy).
> Serwis powinien nasłuchiwać na porcie z zmiennej środowiskowej `PORT` (domyślnie 8080).

**Checkpoint 1a:** Masz katalog `services/[encja]-service/` z kodem źródłowym i `Dockerfile`.

### Skrypt uruchomienia lokalnego

Stwórz plik `services/[encja]-service/run-local.sh`:

Wklej do asystenta:

> Stwórz skrypt `run-local.sh` który:
> 1. Buduje obraz Dockera: `docker build -t [encja]-service .`
> 2. Uruchamia kontener: port 8081, zmienna `PORT=8080`
> 3. Na końcu wypisuje `Service running at http://localhost:8081`
>
> Skrypt powinien obsługiwać argumenty:
> - `./run-local.sh` — buduje i uruchamia
> - `./run-local.sh stop` — zatrzymuje kontener
> - `./run-local.sh logs` — pokazuje logi

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

**Checkpoint 1b:** Serwis zwraca hardkodowane dane JSON na `localhost:8081`. Format odpowiedzi jest identyczny z monolitem.

---

## Krok 2 — Deploy na Cloud Run (hardkodowane dane)

Deployujesz nowy serwis obok monolitu — **nie podmieniasz starego**. Oba działają równolegle.

### Terraform — wydziel infrastrukturę do osobnego pliku

Nie tworzysz nowego projektu Terraform. Pracujesz w tym samym katalogu `infrastructure/`, ale **wydzielasz swoje zasoby do osobnego pliku**.

Wklej do asystenta:

> Mam projekt Terraform w `infrastructure/`.
> Istniejący monolit jest zdefiniowany w [nazwa pliku — sprawdź jak się nazywa].
> Chcę dodać **drugi** Cloud Run service dla mojego nowego serwisu `[encja]-service`.
>
> Stwórz nowy plik `infrastructure/[encja]-service.tf` z:
> 1. `google_cloud_run_v2_service` dla `[encja]-service-dev` (i opcjonalnie prod)
> 2. Użyj **istniejącego** Artifact Registry (nie twórz nowego)
> 3. Cloud Run service musi być publiczny (allow unauthenticated)
> 4. Region: `europe-central2`
>
> Wzoruj się na konfiguracji monolitu — te same patterny, ten sam styl.
> NIE zmieniaj istniejących plików — dodaj nowy plik obok.

### CI/CD — dodaj job do istniejącego workflow

Nie tworzysz nowego workflow. Dodajesz **nowy job** w istniejącym pipeline.

Wklej do asystenta:

> Mam workflow GitHub Actions w `.github/workflows/`.
> Istniejący workflow buduje i deployuje monolit Symfony.
> Chcę dodać **nowy job** w tym samym workflow, który buduje i deployuje `services/[encja]-service/`.
>
> Nowy job powinien:
> 1. Budować obraz Dockera z `services/[encja]-service/`
> 2. Pushować do istniejącego Artifact Registry
> 3. Deployować na Cloud Run service `[encja]-service-dev`
>
> Wzoruj się na istniejącym jobie monolitu. Użyj tych samych secrets i auth.
> Wklej istniejący workflow: [wklej zawartość pliku workflow]

Push i sprawdź:

```bash
git add services/[encja]-service/ infrastructure/
git commit -m "feat([encja]): add [encja]-service skeleton with hardcoded data"
git push origin feat/[encja]-service
```

Po merge do develop — sprawdź Actions i pobierz URL:

```bash
gcloud run services describe [encja]-service-dev --region=europe-central2 --format='value(status.url)'
```

```bash
curl -s https://[SERVICE_URL]/[endpoint] | python3 -m json.tool
```

**Checkpoint 2:** Nowy serwis działa na Cloud Run, zwraca hardkodowane dane. Monolit nadal działa niezależnie.

---

## Krok 3 — Podłączenie do bazy danych (shared database)

Nowy serwis łączy się do **tego samego Cloud SQL** co monolit. Czyta te same tabele.

### Lokalnie

Wklej do asystenta:

> Mam serwis w [TECHNOLOGIA] w `services/[encja]-service/`.
> Chcę podłączyć go do bazy PostgreSQL (Cloud SQL).
> Tabela `[tabela]` już istnieje (stworzona przez migracje monolitu Symfony).
>
> Potrzebuję:
> 1. Sterownik PostgreSQL / ORM / query builder (co pasuje do [FRAMEWORK])
> 2. Konfiguracja połączenia przez zmienną środowiskową `DATABASE_URL`
> 3. Endpoint `GET /[endpoint]` czyta dane z tabeli `[tabela]` zamiast hardkodowanych
> 4. Endpoint `GET /[endpoint]/{id}` czyta pojedynczy rekord po `id`
>
> Format `DATABASE_URL`: `postgresql://user:pass@host:5432/dbname`
> (na Cloud Run będzie inny format z socket — to później)
>
> Schemat tabeli:
> [wklej output z: `psql $DATABASE_URL -c "\d [tabela]"` lub skopiuj z migracji]

Zaktualizuj `run-local.sh` aby przekazywać `DATABASE_URL` do kontenera:

```bash
# W run-local.sh dodaj zmienną:
docker run -e PORT=8080 -e DATABASE_URL="$DATABASE_URL" ...
```

Uruchom Cloud SQL Proxy (jeśli jeszcze nie działa):

```bash
cloud-sql-proxy PROJECT_ID:europe-central2:INSTANCE_NAME --port=5433
```

Uruchom serwis z bazą:

```bash
DATABASE_URL="postgresql://user:pass@host.docker.internal:5433/dbname" ./run-local.sh
```

Sprawdź:

```bash
curl -s http://localhost:8081/[endpoint] | python3 -m json.tool
```

**Checkpoint 3a:** Serwis lokalnie zwraca dane z bazy (te same co monolit na `localhost:8080/[endpoint]`).

### Na Cloud Run

Wklej do asystenta:

> Mam Cloud Run service `[encja]-service-dev` i Cloud SQL instance.
> Monolit już łączy się z Cloud SQL przez Cloud SQL Auth Proxy (flaga `--add-cloudsql-instances`).
> Chcę aby `[encja]-service-dev` też się łączył do tej samej bazy.
>
> W Terraform dodaj:
> 1. Cloud SQL connection annotation na nowym serwisie (jak monolit)
> 2. `DATABASE_URL` jako zmienną środowiskową (format z socket: `postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE`)
> 3. Uprawnienie `roles/cloudsql.client` dla service account nowego serwisu (jeśli używa innego niż monolit)
>
> Hasło do bazy jest w Secret Manager — użyj tego samego sekretu co monolit.

Push, merge, sprawdź:

```bash
curl -s https://[SERVICE_URL]/[endpoint] | python3 -m json.tool
```

**Checkpoint 3b:** Serwis na Cloud Run zwraca dane z Cloud SQL. Odpowiedź identyczna z monolitem.

---

## Krok 4 — Zastąpienie monolitu

Teraz nowy serwis jest gotowy — zwraca te same dane co monolit. Czas na podmianę.

### 4a — Monolit deleguje do nowego serwisu

Zamiast usuwać endpoint z monolitu — niech monolit **przekierowuje** requesty do nowego serwisu.

Wklej do asystenta:

> W monolicie Symfony mam `[ENCJA]Controller` w `src/Controller/[ENCJA]Controller.php`.
> Chcę żeby metoda `index()` zamiast czytać z bazy — robiła HTTP request do nowego serwisu
> i zwracała jego odpowiedź.
>
> Nowy serwis jest dostępny pod URL z zmiennej środowiskowej `[ENCJA]_SERVICE_URL`.
> Użyj `Symfony\Contracts\HttpClient\HttpClientInterface` (autowiring).
>
> Jeśli nowy serwis nie odpowiada (timeout, błąd) — zwróć HTTP 502 z informacją o błędzie.
> Nie rób fallbacku na lokalną bazę — chcemy widzieć kiedy nowy serwis nie działa.

### 4b — Konfiguracja URL

Dodaj zmienną środowiskową w Terraform:

```hcl
# W konfiguracji monolitu (Cloud Run)
env {
  name  = "[ENCJA]_SERVICE_URL"
  value = google_cloud_run_v2_service.[encja]_service.uri
}
```

Lokalnie — dodaj do `.env` monolitu:

```
[ENCJA]_SERVICE_URL=http://host.docker.internal:8081
```

### 4c — Test lokalny

Uruchom oba serwisy:

```bash
# Terminal 1: nowy serwis
cd services/[encja]-service && ./run-local.sh

# Terminal 2: monolit
cd services/symphony-monolith && scripts/local-app.sh up
```

Sprawdź:

```bash
# Monolit deleguje do nowego serwisu
curl -s http://localhost:8080/[endpoint] | python3 -m json.tool

# Nowy serwis bezpośrednio
curl -s http://localhost:8081/[endpoint] | python3 -m json.tool
```

Oba powinny zwracać identyczne dane.

**Checkpoint 4a:** Monolit odpytuje nowy serwis i zwraca jego odpowiedź. Użytkownik nie widzi różnicy.

### 4d — Testy integracyjne

Uruchom istniejące testy — powinny przechodzić bez zmian:

```bash
scripts/local-app.sh test
```

Testy odpytują monolit, monolit deleguje do nowego serwisu, nowy serwis czyta z bazy. Cały chain działa.

**Checkpoint 4b:** Wszystkie istniejące testy integracyjne przechodzą na zielono.

### 4e — Deploy i weryfikacja

```bash
git add .
git commit -m "feat([encja]): delegate [endpoint] from monolith to [encja]-service"
git push origin feat/[encja]-service
```

Po merge i deploy sprawdź na DEV:

```bash
curl -s https://[MONOLITH_DEV_URL]/[endpoint] | python3 -m json.tool
curl -s https://[SERVICE_DEV_URL]/[endpoint] | python3 -m json.tool
```

**Checkpoint 4c (koncowy):** Monolit na DEV deleguje do nowego serwisu. Endpoint zwraca dane z bazy. Testy CI/CD przechodzą.

---

## Podsumowanie: co zrobiliscie

```
Krok 1:  Nowy serwis (hardkodowane dane, lokalnie)
Krok 2:  Deploy na Cloud Run (hardkodowane dane, obok monolitu)
Krok 3:  Podlaczenie do bazy (shared database, lokalnie + Cloud Run)
Krok 4:  Monolit deleguje do nowego serwisu (podmiana)
```

Na diagramie:

```
PRZED:
  Klient → Monolit (PHP) → Cloud SQL

PO:
  Klient → Monolit (PHP) → Nowy serwis (Java/Python/Go/...) → Cloud SQL
```

Monolit staje się cienszą warstwą — deleguje do wyspecjalizowanych serwisów. To jest pierwszy krok migracji.

---

## Troubleshooting

### Nowy serwis nie startuje na Cloud Run

Sprawdź logi:
```bash
gcloud run services logs read [encja]-service-dev --region=europe-central2 --limit=50
```

Najczęstsze przyczyny:
- Serwis nie nasłuchuje na porcie z `$PORT`
- Dockerfile nie buduje się poprawnie (sprawdź lokalnie najpierw)
- Brak uprawnień do Cloud SQL

### Monolit zwraca 502 po podmianie

Sprawdź czy nowy serwis jest dostępny:
```bash
curl -s https://[SERVICE_URL]/[endpoint]
```

Sprawdź czy zmienna `[ENCJA]_SERVICE_URL` jest ustawiona w monolicie:
```bash
gcloud run services describe mini-allegro-dev --region=europe-central2 --format=yaml | grep SERVICE_URL
```

### Dane z nowego serwisu roznia sie od monolitu

Porownaj odpowiedzi:
```bash
diff <(curl -s http://localhost:8080/[endpoint] | python3 -m json.tool) \
     <(curl -s http://localhost:8081/[endpoint] | python3 -m json.tool)
```

Format JSON musi byc identyczny — te same nazwy pol, te same typy. Jesli sie roznia, popraw mapping w nowym serwisie.

---

## Sciagawka: pliki ktore tworzysz / zmieniasz

| Krok | Plik | Akcja |
|------|------|-------|
| 1 | `services/[encja]-service/*` | nowy katalog, kod, Dockerfile |
| 1 | `services/[encja]-service/run-local.sh` | skrypt uruchomienia |
| 2 | `infrastructure/[encja]-service.tf` | nowy plik z Cloud Run service |
| 2 | `.github/workflows/[workflow].yml` | nowy job w istniejącym workflow |
| 3 | `services/[encja]-service/*` | konfiguracja bazy |
| 4 | `src/Controller/[ENCJA]Controller.php` | delegacja do nowego serwisu |
| 4 | `infrastructure/*.tf` | zmienna `[ENCJA]_SERVICE_URL` |
