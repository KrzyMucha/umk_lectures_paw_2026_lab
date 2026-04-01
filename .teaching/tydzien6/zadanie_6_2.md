# Zadanie 6.2: Super Sprzedawca

To zadanie wykonuje **cały zespół razem** — wymaga współpracy, bo feature przecina wszystkie trzy encje.

**Warunek wstępny:** Zadanie 6.1 ukończone przez wszystkich — `Offer`, `User` i `Purchase` muszą być podłączone do bazy.

---

## Wymagania biznesowe

```
1. USER może zostać "Super Sprzedawcą" gdy:
   - Ma więcej niż 100 zakończonych transakcji
   - Ma średnią ocenę > 4.5
   - Konto istnieje > 6 miesięcy

2. OFFER Super Sprzedawcy:
   - Ma odznakę (pole is_super_seller: true)
   - Jest wyżej w wynikach wyszukiwania

3. PURCHASE od Super Sprzedawcy:
   - Zapisuje snapshot: "było od Super Sprzedawcy" w momencie zakupu
   - Ma przedłużoną gwarancję zwrotu: 30 dni zamiast 14

4. Gdy User STRACI status:
   - Jego oferty tracą odznakę
   - Historyczne zamówienia ZACHOWUJĄ informację (snapshot nie zmienia się)
```

---

## Krok 1 — Rozszerzenie encji

### User — dodaj pola kwalifikacji

Wklej do asystenta:

> Do encji `User` w `src/Entity/User.php` dodaj pola:
> - `isSuper: bool` (domyślnie false)
> - `transactionCount: int` (domyślnie 0)
> - `averageRating: float` (domyślnie 0.0)
> - Metodę `meetsSuper(): bool` — zwraca true gdy transactionCount > 100 AND averageRating > 4.5
>   AND konto istnieje > 6 miesięcy (pole `createdAt` już istnieje).
> Dodaj atrybuty ORM i settery. Wzorzec: `Product.php`.

### Offer — dodaj odznakę

Wklej do asystenta:

> Do encji `Offer` w `src/Entity/Offer.php` dodaj pole:
> - `isSuperSeller: bool` (domyślnie false)
> - Metody `markAsSuperSeller()` i `removeSuper()`.
> Dodaj atrybut ORM. Wzorzec: `Product.php`.

### Purchase — dodaj snapshot

Wklej do asystenta:

> Do encji `Purchase` w `src/Entity/Purchase.php` dodaj pola:
> - `wasFromSuperSeller: bool` (domyślnie false)
> - `warrantyDays: int` (domyślnie 14)
> Oba ustawiane w konstruktorze na podstawie stanu Offer w momencie zakupu — już po tym nie zmieniają się.
> Dodaj atrybuty ORM. Wzorzec: `Product.php`.

**Checkpoint 1:** Wszystkie trzy encje mają nowe pola z atrybutami `#[ORM\Column]`.

---

## Krok 2 — Migracja

Wklej do asystenta:

> Trzy encje (`User`, `Offer`, `Purchase`) dostały nowe pola z atrybutami ORM.
> Utwórz migrację `migrations/Version20260401000002.php` z `ALTER TABLE` dla każdej z trzech tabel.
> Metoda `down()` musi cofać wszystkie zmiany. Wzorzec: istniejące migracje w katalogu `migrations/`.

**Checkpoint 2:** Migracja ma `ALTER TABLE` dla `users`, `offers` i `purchases`.

---

## Krok 3 — Serwis logiki

Wklej do asystenta:

> Stwórz `src/Service/SuperSellerService.php` z metodą `updateStatus(User $user): void`:
> 1. Sprawdź `$user->meetsSuper()`.
> 2. Jeśli status się zmienił:
>    - Pobierz przez `OfferRepository` wszystkie oferty tego usera.
>    - Wywołaj `markAsSuperSeller()` lub `removeSuper()` na każdej.
>    - Zapisz zmiany przez `EntityManagerInterface::flush()`.
> 3. Zamówień (Purchase) NIE modyfikuj — snapshot jest niezmienialny.
> Wstrzyknij zależności przez konstruktor (autowiring).

**Checkpoint 3:** Klasa `SuperSellerService` istnieje i kompiluje się (`php bin/console cache:clear`).

---

## Krok 4 — Endpoint sprawdzania kwalifikacji

Wklej do asystenta:

> Do `UserController` dodaj endpoint:
> `POST /users/{id}/check-super`
> Który wywołuje `SuperSellerService::updateStatus()` i zwraca JSON:
> ```json
> { "userId": 1, "isSuper": true, "transactionCount": 120, "averageRating": 4.8 }
> ```
> Wzorzec: istniejące metody w `ProductController`.

**Checkpoint 4:** `curl -X POST http://localhost:8080/users/1/check-super` zwraca JSON (nawet jeśli user nie spełnia kryteriów).

---

## Krok 5 — Snapshot przy zakupie

Upewnij się że w `PurchaseController::create()` (lub serwisie tworzącym zakup):

```php
$purchase->setWasFromSuperSeller($offer->isSuperSeller());
$purchase->setWarrantyDays($offer->isSuperSeller() ? 30 : 14);
```

**Checkpoint 5:** Tworzenie Purchase przez POST ustawia `warrantyDays: 30` gdy oferta ma `isSuperSeller: true`.

---

## Krok 6 — Test integracyjny Super Sprzedawcy

Wklej do asystenta:

> Dodaj plik `integ-tests/test_super_seller.py` z testem scenariusza end-to-end:
> 1. Utwórz Usera przez POST `/users` z `transactionCount=120`, `averageRating=4.9`.
> 2. Wywołaj POST `/users/{id}/check-super` — sprawdź `isSuper: true`.
> 3. Utwórz Offer przez POST `/offers` dla tego Usera — sprawdź `isSuperSeller: true`.
> 4. Utwórz Purchase przez POST `/purchases` na tę Offer — sprawdź `warrantyDays: 30` i `wasFromSuperSeller: true`.
> 5. Zmień transactionCount Usera na 50 (przez endpoint lub bezpośrednio), wywołaj check-super ponownie.
> 6. Sprawdź GET `/offers` — oferta powinna mieć `isSuperSeller: false`.
> 7. Sprawdź GET `/purchases/{id}` — `wasFromSuperSeller` nadal `true` (snapshot!).
> Wzorzec: `test_products.py` i `_api_client.py`.

**Checkpoint 6:** Test `test_super_seller.py` ma funkcje `test_*` pokrywające kroki 1–7.

---

## Krok 7 — Uruchom i zweryfikuj lokalnie

```bash
scripts/local-app.sh restart
scripts/local-app.sh test
```

**Checkpoint 7 (końcowy lokalny):** Wszystkie testy zielone, w tym `test_super_seller.py`.

---

## Krok 8 — Deploy

```bash
git add .
git commit -m "feat(super-seller): cross-entity Super Seller feature"
git push origin develop
```

**Checkpoint 8:** Workflow `Deploy DEV` → `Deploy PROD` zielony ✅.

---

## Pytania do refleksji

Po ukończeniu zastanów się:

1. **Snapshot vs live data** — co by się stało gdyby `Purchase` czytał status Usera przez JOIN zamiast zapisywać `wasFromSuperSeller` przy zakupie?

2. **Własność danych** — kto jest "źródłem prawdy" o statusie Super Sprzedawcy? Czy `Offer` powinna decydować sama o swojej odznace?

3. **Co jeśli system rozrośnie się do milionów ofert?** — `SuperSellerService` iteruje po wszystkich ofertach Usera. Jak to zoptymalizować?
