# Zadanie 6.1: Podłączenie encji do bazy danych

Każdy student pracuje z **jedną wylosowaną encją** (`Offer`, `User` lub `Purchase`).
Wszędzie gdzie widzisz `[ENCJA]`, podstaw nazwę swojej encji.
Wzorzec do naśladowania to już działająca encja `Product` — zaglądaj do niej w razie wątpliwości.

Pracujesz **krok po kroku**. Po każdym kroku jest checkpoint — nie przechodź dalej zanim nie zobaczysz że działa.

---

## Zanim zaczniesz — praca z gitem

Każdy student pracuje na **własnym branchu**. Dzięki temu nie nadpiszecie sobie nawzajem zmian.

### Utwórz swój branch

```bash
git checkout develop
git pull origin develop
git checkout -b feat/[encja_lowercase]-entity
```

Przykłady: `feat/offer-entity`, `feat/user-entity`, `feat/purchase-entity`.

### Unikalna nazwa migracji

Każdy ma przydzielony numer — użyj go w nazwie pliku migracji, żeby uniknąć konfliktu:

| Encja | Numer migracji |
|-------|----------------|
| Offer | `Version20260401000001.php` |
| User | `Version20260401000002.php` |
| Purchase | `Version20260401000003.php` |

### Przed każdym pushem

```bash
git pull origin develop --rebase
```

Jeśli pojawi się konflikt — prawie na pewno dotyczy pliku który nie jest Twój. Wklej do asystenta:

> Mam konflikt w gicie po `git pull --rebase`. Plik z konfliktem: [nazwa pliku].
> Zawartość: [wklej sekcję z `<<<<<<<` do `>>>>>>>`]
> Pomóż rozwiązać konflikt bez utraty moich zmian.

---

## Krok 1 — Dodaj mapowanie Doctrine ORM do encji

Otwórz plik `services/symphony-monolith/src/Entity/[ENCJA].php`.
Wklej do asystenta:

> Mam projekt Symfony z encją `[ENCJA]` w pliku `src/Entity/[ENCJA].php`.
> Encja nie ma jeszcze mapowania Doctrine ORM (brak atrybutów `#[ORM\...]`).
> Wzorzec jak to powinno wyglądać znajdziesz w `src/Entity/Product.php`, które już ma pełne mapowanie.
> Dodaj do encji `[ENCJA]` atrybuty ORM (`#[ORM\Entity]`, `#[ORM\Column]` itp.) dla wszystkich pól.
> Dodaj też właściwości `settery` tam gdzie ich brakuje (wzoruj się na `Product`).
> Nie zmieniaj logiki biznesowej ani metod `toArray()`.

**Checkpoint 1:** Otwórz zmodyfikowany plik i sprawdź, że każde pole ma atrybut `#[ORM\Column]`, a nad klasą jest `#[ORM\Entity(...)]`.

---

## Krok 2 — Utwórz klasę Repository

Wzorzec: `src/Repository/ProductRepository.php`.
Wklej do asystenta:

> W projekcie Symfony istnieje już `src/Repository/ProductRepository.php`.
> Stwórz analogiczną klasę `[ENCJA]Repository` w `src/Repository/[ENCJA]Repository.php`
> dla encji `App\Entity\[ENCJA]`.
> Wzoruj się dokładnie na `ProductRepository`.

**Checkpoint 2:** Plik `src/Repository/[ENCJA]Repository.php` istnieje i klasa dziedziczy po `ServiceEntityRepository`.

---

## Krok 3 — Wygeneruj migrację bazy danych

Wklej do asystenta:

> W projekcie Symfony z Doctrine Migrations chcę dodać tabelę dla encji `[ENCJA]`.
> Istniejące migracje są w `services/symphony-monolith/migrations/`.
> Najnowsza to `Version20260330000003.php` — nowa musi mieć późniejszą datę/numer.
> Na podstawie pól encji `[ENCJA]` (z jej atrybutami `#[ORM\Column]`) utwórz nową migrację
> w pliku `migrations/[TWÓJ_NUMER_MIGRACJI].php` z metodami `up()` oraz `down()`.
> (Numer migracji znajdziesz w tabeli na początku zadania — każda encja ma inny, żeby uniknąć konfliktów git.)
> Wzoruj się na istniejących migracjach. Użyj czystego SQL (`$this->addSql(...)`).

**Checkpoint 3:** Plik migracji istnieje w katalogu `migrations/`.
Sprawdź że metoda `up()` ma `CREATE TABLE`, a `down()` ma `DROP TABLE`.

---

## Krok 4 — Podłącz Repository do Controllera

Otwórz `src/Controller/[ENCJA]Controller.php`.
Aktualnie zwraca dane z hardkodowanej tablicy (mock). Wklej do asystenta:

> W projekcie Symfony mam kontroler `[ENCJA]Controller` w `src/Controller/[ENCJA]Controller.php`.
> Aktualnie metoda `index()` zwraca hardkodowaną tablicę obiektów (mock data).
> Chcę podłączyć go do bazy danych przez `[ENCJA]Repository` (wzorzec: `ProductController` + `ProductRepository`).
>
> 1. Wstrzyknij `[ENCJA]Repository` przez konstruktor (autowiring).
> 2. W metodzie `index()` zastąp mock data wywołaniem `$this->[encja]Repository->findAll()`.
> 3. Zachowaj istniejące logowanie i kształt odpowiedzi JSON (korzystaj z `toArray()`).
> 4. Jeśli kontroler ma metody `create()` / `store()` jako mock — podłącz je przez `EntityManagerInterface`
>    analogicznie jak `ProductController::create()`.

**Checkpoint 4:** Kontroler nie zawiera już hardkodowanych tablic `$items = [new [ENCJA](...)...]`.

---

## Krok 5 — Test lokalny (uruchomienie)

```bash
scripts/local-app.sh up
```

Poczekaj aż kontener jest zdrowy, następnie:

```bash
curl -s http://localhost:8080/[endpoint] | python3 -m json.tool
```

> Wskazówka: endpoint to lowercase nazwa encji w liczbie mnogiej, np. `/offers`, `/users`, `/purchases`.

**Checkpoint 5:**
- Odpowiedź to lista JSON (pusta `[]` jest OK — tabela dopiero powstała).
- Brak błędu 500.
- W logach kontenera (`scripts/local-app.sh logs`) widać że migracja przeszła.

Jeśli widzisz błąd 500 — wklej do asystenta:

> Uruchomiłem `scripts/local-app.sh up` i dostałem błąd 500 na endpoincie `/[endpoint]`.
> Logi kontenera: [wklej output z `scripts/local-app.sh logs`]
> Pomóż mi zdebugować.

---

## Krok 6 — Dodaj/zaktualizuj test integracyjny

Otwórz `integ-tests/test_[encja_lowercase].py`. Wzorzec: `integ-tests/test_products.py`.
Wklej do asystenta:

> W projekcie mamy testy integracyjne w Pythonie w katalogu `integ-tests/`.
> Wzorzec testu to `test_products.py` — robi POST, sprawdza odpowiedź, potem GET i weryfikuje że rekord jest na liście.
> Pomocnik HTTP jest w `_api_client.py` (funkcja `request_json`).
>
> Zaktualizuj `integ-tests/test_[encja_lowercase].py` tak żeby:
> 1. Test `GET /[endpoint]` sprawdzał kształt odpowiedzi (czy zwraca listę, jakie pola mają rekordy).
> 2. Jeśli endpoint obsługuje `POST` — dodaj test roundtrip: stwórz rekord przez POST, sprawdź ID,
>    zweryfikuj przez GET że jest na liście.
> 3. Użyj `uuid.uuid4().hex[:8]` do generowania unikalnych wartości testowych.
>
> Istniejące encje i ich pola: [wklej zawartość pliku Entity/[ENCJA].php]

**Checkpoint 6:** Plik `integ-tests/test_[encja_lowercase].py` ma co najmniej jedną funkcję `test_*`.

---

## Krok 7 — Testowanie ręczne i testy integracyjne

### 7a — Sprawdź ręcznie curlem

```bash
# Pobierz listę
curl -s http://localhost:8080/[endpoint] | python3 -m json.tool

# Utwórz rekord (jeśli endpoint obsługuje POST)
curl -s -X POST http://localhost:8080/[endpoint] \
  -H "Content-Type: application/json" \
  -d '{"name": "test-abc123"}' | python3 -m json.tool

# Pobierz listę ponownie — sprawdź że rekord jest
curl -s http://localhost:8080/[endpoint] | python3 -m json.tool
```

**Checkpoint 7a:** Widzisz rekord na liście, odpowiedź ma oczekiwane pola JSON.

### 7b — Uruchom testy integracyjne lokalnie

```bash
scripts/local-app.sh test
```

**Checkpoint 7b:** Wszystkie testy przechodzą (zielony output pytest).

Jeśli testy failują — wklej do asystenta:

> Testy integracyjne (`scripts/local-app.sh test`) failują.
> Output pytest: [wklej]
> Plik testu: [wklej zawartość test_[encja_lowercase].py]
> Kontroler: [wklej zawartość [ENCJA]Controller.php]
> Pomóż naprawić.

---

## Krok 8 — Pull Request i deploy DEV przez CI/CD

```bash
git add .
git commit -m "feat([encja_lowercase]): connect [ENCJA] entity to database"
git pull origin develop --rebase
git push origin feat/[encja_lowercase]-entity
```

Otwórz GitHub → **Pull Requests** → **New pull request**.
- Base: `develop` ← Compare: `feat/[encja_lowercase]-entity`
- Tytuł: `feat([encja_lowercase]): connect [ENCJA] entity to database`

Po zatwierdzeniu PR i merge do `develop` otwórz zakładkę **Actions** i obserwuj workflow **Deploy DEV**.

**Checkpoint 8:** Workflow `Deploy DEV` zakończony zielonym statusem ✅.
Wszystkie joby przeszły: `validate-secrets` → `terraform-dev` → `build-dev` → `deploy-dev` → `integration-tests-dev` → `promote-to-main`.

Jeśli deploy failuje — wklej do asystenta:

> GitHub Actions workflow `Deploy DEV` failuje na jobie `[nazwa joba]`.
> Logi błędu: [wklej ze strony Actions]
> Pomóż mi zdebugować.

---

## Krok 9 — Weryfikacja na DEV i PROD

Po przejściu `Deploy DEV` automatycznie startuje **Deploy PROD** (merge `develop → main`).

Pobierz URL serwisu:
```bash
gcloud run services describe mini-allegro-dev --region=europe-central2 --format='value(status.url)'
gcloud run services describe mini-allegro-prod --region=europe-central2 --format='value(status.url)'
```

Sprawdź endpoint na obu środowiskach:
```bash
curl -s https://[DEV_URL]/[endpoint] | python3 -m json.tool
curl -s https://[PROD_URL]/[endpoint] | python3 -m json.tool
```

**Checkpoint 9 (końcowy):**
- Endpoint zwraca `200 OK` na DEV ✅
- Endpoint zwraca `200 OK` na PROD ✅
- Dane przychodzą z bazy danych (nie są hardkodowane) ✅

---

## Ściągawka: pliki które zmieniasz

| Krok | Plik |
|------|------|
| 1 | `src/Entity/[ENCJA].php` |
| 2 | `src/Repository/[ENCJA]Repository.php` (nowy) |
| 3 | `migrations/Version202604010000XX.php` (nowy) |
| 4 | `src/Controller/[ENCJA]Controller.php` |
| 6 | `integ-tests/test_[encja_lowercase].py` |

**Pliki których NIE dotykasz:** `doctrine.yaml`, `services.yaml`, `Dockerfile`, workflow CI/CD.

## Ściągawka: gotowe encje do podglądu

| Twój plik | Wzorzec |
|-----------|---------|
| `Entity/[ENCJA].php` | `Entity/Product.php` |
| `Repository/[ENCJA]Repository.php` | `Repository/ProductRepository.php` |
| `Controller/[ENCJA]Controller.php` | `Controller/ProductController.php` |
| `integ-tests/test_[encja_lowercase].py` | `integ-tests/test_products.py` |
