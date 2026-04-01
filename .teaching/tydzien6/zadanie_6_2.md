# Zadanie 6.2: Wspólna encja SuperSeller

To zadanie wykonuje **cały zespół razem**.

**Warunek wstępny:** Zadanie 6.1 ukończone przez wszystkich.

Cel: stworzyć nową encję `SuperSeller` i dodać do każdej istniejącej encji relację (FK) do niej.

---

## Krok 1 — Nowa encja SuperSeller

Jedna osoba tworzy encję. Pozostałe czekają na merge przed Krokiem 3.

Wklej do asystenta:

> Stwórz nową encję `src/Entity/SuperSeller.php` w projekcie Symfony z Doctrine ORM.
> Pola:
> - `id: int` (klucz główny, autoinkrementowany)
> - `name: string`
> - `isActive: bool` (domyślnie true)
> - `createdAt: \DateTimeImmutable`
> Dodaj pełne mapowanie Doctrine ORM i settery. Wzorzec: `Product.php`.
> Stwórz też `src/Repository/SuperSellerRepository.php`. Wzorzec: `ProductRepository.php`.

Commit i push na `develop`:

```bash
git add .
git commit -m "feat(super-seller): add SuperSeller entity"
git push origin develop
```

**Checkpoint 1:** Plik `src/Entity/SuperSeller.php` i `src/Repository/SuperSellerRepository.php` są na `develop`.

---

## Krok 2 — Pozostali pobierają zmiany

Każdy student (Offer, User, Purchase) przed przystąpieniem do Kroku 3:

```bash
git pull origin develop
```

**Checkpoint 2:** Widzisz plik `src/Entity/SuperSeller.php` u siebie lokalnie.

---

## Krok 3 — Dodaj FK do swojej encji

Każdy student dodaje relację do `SuperSeller` w swojej encji.

Wklej do asystenta:

> Do encji `[ENCJA]` w `src/Entity/[ENCJA].php` dodaj nullable relację `#[ORM\ManyToOne]`
> do `App\Entity\SuperSeller` (pole `superSeller: ?SuperSeller`, domyślnie null).
> Dodaj getter i setter. Wzorzec stylu atrybutów: `Product.php`.

**Checkpoint 3:** Pole `superSeller` z atrybutem `#[ORM\ManyToOne]` jest w Twojej encji.

---

## Krok 4 — Migracja

Jedna osoba (lub każdy osobno) tworzy migrację dla swojej tabeli.

Wklej do asystenta:

> W projekcie Symfony z Doctrine Migrations dodaj migrację dla tabeli `[ENCJA]`.
> Encja `[ENCJA]` dostała nowe pole `superSeller: ?SuperSeller` (ManyToOne FK do tabeli `super_sellers`).
> Utwórz migrację `migrations/[TWÓJ_NUMER_MIGRACJI_Z_TABELI].php` z:
> - `up()`: `ALTER TABLE [tabela] ADD super_seller_id INT NULL` + klucz obcy do `super_sellers`
> - `down()`: cofa zmiany
> Wzorzec: istniejące migracje.

> Numer migracji per encja (żeby uniknąć konfliktów):

| Encja | Numer migracji |
|-------|----------------|
| SuperSeller (Krok 1) | `Version20260401000004.php` |
| Offer | `Version20260401000005.php` |
| User | `Version20260401000006.php` |
| Purchase | `Version20260401000007.php` |

**Checkpoint 4:** Migracja ma `ALTER TABLE ... ADD super_seller_id`.

---

## Krok 5 — Endpoint GET /[encja]-super

Każdy student dodaje endpoint do swojego kontrolera. Semantyka różni się per encja:

| Encja | Endpoint | Co zwraca |
|-------|----------|-----------|
| User | `GET /users-super` | Userzy którzy **są** SuperSellersami (`superSeller IS NOT NULL`) |
| Offer | `GET /offers-super` | Oferty które **należą do** SuperSellera (`superSeller IS NOT NULL`) |
| Purchase | `GET /purchases-super` | Zakupy które **zostały zrobione od** SuperSellera (`superSeller IS NOT NULL`) |

Wklej do asystenta odpowiedni prompt dla swojej encji:

**User:**
> Do `UserController` dodaj endpoint `GET /users-super`.
> Zwraca listę Userów którzy są SuperSellersami (`superSeller IS NOT NULL`).
> Użyj `UserRepository::findBy` lub DQL. Format jak `GET /users`, dodaj pole `superSellerId`.

**Offer:**
> Do `OfferController` dodaj endpoint `GET /offers-super`.
> Zwraca listę Ofert należących do SuperSellera (`superSeller IS NOT NULL`).
> Użyj `OfferRepository::findBy` lub DQL. Format jak `GET /offers`, dodaj pole `superSellerId`.

**Purchase:**
> Do `PurchaseController` dodaj endpoint `GET /purchases-super`.
> Zwraca listę Zakupów zrobionych od SuperSellera (`superSeller IS NOT NULL`).
> Użyj `PurchaseRepository::findBy` lub DQL. Format jak `GET /purchases`, dodaj pole `superSellerId`.

**Checkpoint 5:**
```bash
curl -s http://localhost:8080/users-super | python3 -m json.tool
curl -s http://localhost:8080/offers-super | python3 -m json.tool
curl -s http://localhost:8080/purchases-super | python3 -m json.tool
```
Każdy zwraca `200 OK` z pustą listą `[]`.

---

## Krok 6 — Deploy

```bash
git add .
git commit -m "feat([encja_lowercase]): add SuperSeller FK and -super endpoint"
git pull origin develop --rebase
git push origin feat/[encja_lowercase]-entity
```

Otwórz PR na `develop` jak w zadaniu 6.1.

**Checkpoint 6:** Workflow `Deploy DEV` → `Deploy PROD` zielony ✅.

---

## Pytania do refleksji

1. Każda z trzech encji zależy teraz od `SuperSeller`. Co się stanie jeśli ktoś zmieni schemat tabeli `super_sellers`?
2. Czy `Offer`, `User` i `Purchase` powinny wiedzieć o sobie nawzajem? A o `SuperSeller`?
3. Jak wyglądałoby to gdyby każda encja była w osobnym serwisie z własną bazą danych?
