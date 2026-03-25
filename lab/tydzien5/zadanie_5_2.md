# Zadanie 5.2: Model domenowy

Zaimplementuj encje z relacjami, migracje, endpointy i dane testowe.

## Schema

```
User
  id, email, name
  type: enum(seller | buyer)

Offer
  id, title, price, description
  seller → User[type=seller]

Purchase
  id, price, created_at
  offer  → Offer
  buyer  → User[type=buyer]

Opinion                        (jeśli masz z poprzedniego tygodnia)
  id, rating, text
  offer  → Offer
  buyer  → User[type=buyer]
```

## Co zrobić

Dla każdej encji:
- klasa Doctrine z relacjami (`ManyToOne`)
- migracja
- endpoint `POST` (tworzy zasób) i `GET` (zwraca listę)

Przy tworzeniu zasobu waliduj typ użytkownika - seller nie może być buyer przy zakupie i na odwrót.

Na końcu załaduj seed data: kilku użytkowników obu typów, kilka ofert, zakupów i opinii.

## Wskazówki

- `php bin/console make:entity` i `make:migration` przyspieszają robotę
- Relacje Doctrine: `#[ORM\ManyToOne]` z `inversedBy` / `mappedBy`
- Seed data najwygodniej przez Doctrine Fixtures (`doctrine/doctrine-fixtures-bundle`)
- Walidacja typu: można w kontrolerze lub jako własny Doctrine constraint

## Checkpoint

- [ ] Encje z relacjami - migracje wykonane na dev i prod
- [ ] `POST /users`, `GET /users`
- [ ] `POST /offers`, `GET /offers`
- [ ] `POST /purchases`, `GET /purchases`
- [ ] Walidacja typu użytkownika działa (błąd gdy seller próbuje kupić)
- [ ] Seed data załadowane - baza ma przykładowe dane
