# Lab 4: CI/CD, Monitoring i Testy

## Zadanie 1: CI/CD Pipeline

Skonfiguruj automatyczny deployment aplikacji Symfony z tygodnia 3.

- Stwórz branch `develop`
- Napisz GitHub Actions workflow (`.github/workflows/deploy.yml`) który:
  - buduje obraz Docker i pushuje do Artifact Registry
  - po pushu na `develop` → automatycznie deployuje na Cloud Run DEV
  - po pushu na `main` → deployuje na DEV, czeka na ręczne zatwierdzenie, potem deployuje na PROD
  - sprawdza po deployu czy serwis odpowiada HTTP 200
- Dodaj sekrety `GCP_PROJECT_ID` i `GCP_SA_KEY` do repo
- Skonfiguruj GitHub Environments: `dev` (auto) i `prod` (wymagany reviewer)

**Efekt:** push do `develop` → aplikacja dostępna na Cloud Run DEV bez żadnej ręcznej akcji.

---

## Zadanie 2: Monitoring i Alerty

Skonfiguruj monitoring aplikacji produkcyjnej.

- W Google Cloud Monitoring utwórz Uptime Check sprawdzający `/offers` co minutę
- Utwórz Alert Policy która wysyła email gdy serwis nie odpowiada przez 5 minut
- Przetestuj: zepsuj endpoint (zmień path w uptime check na nieistniejący) → poczekaj na email alertowy → przywróć → poczekaj na email "resolved"

**Efekt:** gdy PROD padnie, dostajesz email w ciągu 5 minut.

---

## Zadanie 3: Logi i Cloud Logging

Dodaj structured logging do aplikacji i skonfiguruj alert oparty na logach.

- Skonfiguruj Monolog żeby pisał JSON na stdout
- Dodaj do kontrolerów logi z kontekstem (np. `offer_id`, liczba wyników) - nie loguj danych osobowych
- Sprawdź logi w Cloud Logging Log Explorer, przefiltruj po `severity>=WARNING`
- Utwórz Log-based Metric zliczającą ERROR logi z Cloud Run
- Utwórz Alert Policy który triggeruje gdy pojawi się 5+ errorów w 5 minut

**Efekt:** błędy aplikacji widoczne w Cloud Logging + alert emailowy przy ich nagromadzeniu.

---

## Zadanie 4: Rollback i testy integracyjne

### Część A: Rollback

Zasymuluj incident produkcyjny i wykonaj rollback.

- Wdróż celowo zepsutą wersję na PROD (np. `throw new RuntimeException()` w kontrolerze)
- Poczekaj na alert emailowy z zadania 2
- Wykonaj rollback przez `gcloud run services update-traffic` do poprzedniej revizji
- Zweryfikuj że serwis działa poprawnie

### Część B: Testy integracyjne z auto-rollbackiem

Zabezpiecz pipeline żeby taki incydent nie mógł się powtórzyć.

- Napisz testy PHPUnit (`tests/Controller/OfferControllerTest.php`) pokrywające podstawowe endpointy
- Napisz skrypt `scripts/smoke_test.sh` który odpytuje HTTP realne URL serwisu
- Rozbuduj workflow o job `test` uruchamiany przed buildem
- Dodaj job `smoke-test-dev` po deployu na DEV który: uruchamia smoke testy, a w razie niepowodzenia cofa deployment i blokuje wejście na PROD

Przetestuj dwa scenariusze:
1. Czerwone testy jednostkowe → pipeline zatrzymuje się przed buildem
2. Smoke testy failują → DEV wraca do poprzedniej wersji, PROD zablokowany

**Efekt:** pipeline który sam cofa złe deploymenty zanim dotrą na PROD.
