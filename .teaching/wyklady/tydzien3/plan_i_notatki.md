# Tydzień 3: Wykład

## Temat
CRUD, monolity i era PHP - jak budowano aplikacje webowe

## Kontekst
Wykład odbywa się gdy studenci pracują nad Symfony CRUD. Pokazujemy historyczny kontekst i wyjaśniamy dlaczego ta architektura była (i często nadal jest) sensownym wyborem.

## Cel wykładu
- Zrozumieć czym jest architektura CRUD i skąd się wzięła
- Poznać historię rozwoju aplikacji webowych (lata 2000-2010)
- Zobaczyć jak wielkie firmy (Facebook, Allegro) zaczynały od prostych rozwiązań
- Zrozumieć ograniczenia monolitów i problemy ze skalowaniem

---

## Plan wykładu (~70 min)

### 1. Refleksja: co właśnie robicie na labach? (~5 min)

**Pytania do studentów:**
- "Budujecie Symfony z encjami, kontrolerami, bazą danych - czy wiecie jak nazywa się ta architektura?"
- "Czy to jest 'stara' czy 'nowa' technologia?"
- "Czy duże firmy tak budują swoje systemy?"

---

## CRUD - fundamentalna architektura aplikacji

### 2. Czym jest CRUD? (~10 min)

**Definicja:**
CRUD to akronim opisujący cztery podstawowe operacje na danych:

| Operacja | SQL | HTTP | Opis |
|----------|-----|------|------|
| **C**reate | INSERT | POST | Tworzenie nowych rekordów |
| **R**ead | SELECT | GET | Odczytywanie danych |
| **U**pdate | UPDATE | PUT/PATCH | Modyfikowanie istniejących |
| **D**elete | DELETE | DELETE | Usuwanie rekordów |

**Architektura CRUD:**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Przeglądarka │────▶│  Aplikacja  │────▶│    Baza     │
│  (UI)        │◀────│  (PHP/Java) │◀────│   danych    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              Kontrolery    Modele (ORM)
                    │             │
                    └─────────────┘
```

**Kluczowa cecha:**
> Aplikacja CRUD to w istocie "inteligentny interfejs do bazy danych". Logika biznesowa jest minimalna - głównie walidacja i transformacja danych.

**To co robicie na labach:**
- Encja `Offer` → tabela `offers` w bazie
- `OfferController` → endpointy CRUD
- Doctrine ORM → mapowanie obiektowo-relacyjne

---

### 3. CRUD to nie jest zła architektura (~10 min)

**Powszechne nieporozumienie:**
> "CRUD jest przestarzały, trzeba używać mikroserwisów"

**Prawda:**
CRUD to **sprawdzona, prosta architektura** która:
- Jest łatwa do zrozumienia i nauczenia
- Dobrze mapuje się na operacje bazodanowe
- Wystarczy dla większości aplikacji biznesowych
- Ma świetne wsparcie narzędziowe

**Kiedy CRUD jest idealny:**
- Systemy CRUD-owe (CRM, ERP, panele administracyjne)
- Aplikacje z prostą logiką biznesową
- MVP i prototypy
- Małe i średnie zespoły
- Aplikacje wewnętrzne

**Przykłady gdzie CRUD wystarczy:**
- System zarządzania pracownikami
- Katalog produktów
- Blog, CMS
- Panel administracyjny
- Większość aplikacji biznesowych!

> **80% aplikacji biznesowych to gloryfikowane CRUDy.** I nie ma w tym nic złego.

---

## Historia: jak budowano aplikacje webowe

### 4. Era przed ORM (lata 90. - wczesne 2000.) (~10 min)

**Jak to wyglądało:**

```php
<?php
// Rok 1999 - "czysty" PHP
$conn = mysql_connect("localhost", "user", "pass");
mysql_select_db("shop");

$result = mysql_query("SELECT * FROM products WHERE id = " . $_GET['id']);
// SQL Injection? Co to? 🙈

$row = mysql_fetch_array($result);
echo "<h1>" . $row['name'] . "</h1>";
echo "<p>Cena: " . $row['price'] . " zł</p>";
?>
```

**Problemy:**
- SQL pisany ręcznie, wszędzie
- Brak separacji warstw (HTML + SQL + PHP w jednym pliku)
- SQL Injection jako standard
- Duplikacja kodu
- Brak możliwości testowania

**Ale działało!**
- Proste do uruchomienia (FTP na serwer)
- Tanie hostingi PHP
- Szybkie prototypowanie
- Niska bariera wejścia

---

### 5. Rewolucja ORM i frameworków (2004-2010) (~15 min)

#### Hibernate (Java, 2001) - przełom

**Idea:**
> "Niech framework zajmie się SQL-em. Programista pracuje z obiektami."

```java
// Zamiast SQL:
// SELECT * FROM users WHERE email = 'jan@example.com'

// Piszemy:
User user = session.createQuery(
    "FROM User WHERE email = :email")
    .setParameter("email", "jan@example.com")
    .uniqueResult();
```

**Co dał Hibernate:**
- **Object-Relational Mapping (ORM)** - obiekty ↔ tabele
- **Lazy loading** - dane ładowane na żądanie
- **Caching** - automatyczna pamięć podręczna
- **Transakcje** - zarządzanie spójnością
- **Migracje** - ewolucja schematu

#### Rozwój baz relacyjnych

**MySQL (1995, ale rozkwit 2000+):**
- Darmowa, szybka, "wystarczająco dobra"
- LAMP stack: Linux + Apache + MySQL + PHP
- Używana przez: Facebook, Twitter, YouTube (na początku)

**PostgreSQL (1996, dojrzałość ~2005):**
- "Enterprise features" za darmo
- Transakcje ACID, zaawansowane typy danych
- Lepsza zgodność ze standardami SQL
- Używana przez: Instagram, Spotify, Reddit

**Porównanie:**
| Cecha | MySQL | PostgreSQL |
|-------|-------|------------|
| Filozofia | Szybkość, prostota | Poprawność, funkcjonalność |
| Licencja | GPL (Oracle) | BSD (wolna) |
| JSON | Od 5.7 (2015) | Od 9.2 (2012), lepszy |
| Replikacja | Master-slave | Multi-master, streaming |

#### Frameworki MVC

**Ruby on Rails (2004) - "Convention over Configuration":**
```ruby
# To wystarczy żeby mieć pełny CRUD:
class Product < ApplicationRecord
  belongs_to :category
  validates :name, presence: true
end
```

**Symfony (PHP, 2005):**
- Profesjonalny framework PHP
- Doctrine ORM (inspirowany Hibernate)
- **To czego używacie na labach!**

**Django (Python, 2005):**
- "The web framework for perfectionists with deadlines"
- Wbudowany ORM, admin panel

**Spring (Java, 2002):**
- Enterprise Java bez bólu J2EE
- Spring Boot (2014) - jeszcze prościej

#### Wzorzec MVC

```
┌─────────────────────────────────────────────────────┐
│                    MVC Pattern                       │
│                                                     │
│  ┌─────────┐    ┌─────────────┐    ┌─────────┐    │
│  │  Model  │◀──▶│ Controller  │◀──▶│  View   │    │
│  │ (dane)  │    │  (logika)   │    │  (UI)   │    │
│  └────┬────┘    └─────────────┘    └─────────┘    │
│       │                                            │
│       ▼                                            │
│  ┌─────────┐                                       │
│  │   ORM   │                                       │
│  └────┬────┘                                       │
│       │                                            │
│       ▼                                            │
│  ┌─────────┐                                       │
│  │   DB    │                                       │
│  └─────────┘                                       │
└─────────────────────────────────────────────────────┘
```

---

### 6. Facebook i Allegro - zaczynały od PHP (~10 min)

#### Facebook (2004)

**Początki:**
- Mark Zuckerberg, pokój w akademiku Harvard
- Czysty PHP, MySQL
- Jeden serwer

**Ewolucja:**
```
2004: PHP + MySQL (1 serwer)
      ↓
2007: PHP + MySQL + Memcached (tysiące serwerów)
      ↓
2010: HipHop (PHP → C++) - 50% oszczędności CPU
      ↓
2014: HHVM (własna maszyna wirtualna PHP)
      ↓
2020+: Hack (własny język bazowany na PHP)
```

**Kluczowa lekcja:**
> Facebook nie przepisał wszystkiego na Javę/Go/Rust. **Zoptymalizował PHP.**
> "Boring technology" która działa > "Sexy technology" która nie skaluje

**Skala Facebook (2024):**
- ~3 miliardy użytkowników
- Setki tysięcy serwerów
- Nadal dużo kodu w Hack (pochodna PHP)

#### Allegro (1999)

**Początki:**
- Polska aukcja internetowa
- PHP + MySQL
- Klasyczna architektura LAMP

**Ewolucja:**
```
1999: PHP + MySQL (monolit)
      ↓
2010: Nadal PHP, ale problemy ze skalą
      ↓
2015: Podział na mikroserwisy
      ↓
2020+: ~1000 mikroserwisów
       Własna platforma (nie chmura publiczna)
       Kotlin, Java, Go
```

**Kluczowa lekcja:**
> Allegro zaczęło jako prosty monolit PHP. Mikroserwisy przyszły **gdy było to potrzebne**, nie na początku.

#### Dlaczego PHP był tak popularny?

| Cecha | Korzyść |
|-------|---------|
| Niski próg wejścia | Szybki start, łatwa nauka |
| Tanie hostingi | $5/miesiąc wystarczało |
| Deploy = FTP | Brak skomplikowanego CI/CD |
| Duża społeczność | Stackoverflow, tutoriale |
| Działało | "Good enough" dla większości |

---

## Problemy ze skalowaniem monolitu

### 7. Architektura monolityczna - definicja i cechy (~5 min)

**Czym jest monolit:**
```
┌─────────────────────────────────────────┐
│              MONOLIT                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Moduł A │ │ Moduł B │ │ Moduł C │   │
│  │ (Users) │ │ (Orders)│ │(Payments)│   │
│  └────┬────┘ └────┬────┘ └────┬────┘   │
│       │          │           │         │
│       └──────────┼───────────┘         │
│                  ▼                      │
│           Wspólna baza danych           │
│              (1 instancja)              │
└─────────────────────────────────────────┘
```

**Cechy monolitu:**
- Jeden deployment (jedna aplikacja)
- Wspólna baza danych
- Wspólny kod (wszystko w jednym repo)
- Wspólne skalowanie (cała aplikacja albo nic)

**To co robicie na labach = monolit** (i to jest OK na tym etapie!)

---

### 8. Problemy ze skalowaniem (~10 min)

#### Problem 1: Skalowanie "wszystko albo nic"

```
Obciążenie:
- Moduł Users: 10 req/s
- Moduł Orders: 1000 req/s  ← wąskie gardło
- Moduł Reports: 1 req/s

W monolicie: Musisz skalować CAŁĄ aplikację
W mikroserwisach: Skalujesz tylko Orders
```

#### Problem 2: Jeden deployment = jeden punkt awarii

```
Błąd w module Payments
        ↓
Pada CAŁA aplikacja
        ↓
Users, Orders, Reports - wszystko niedostępne
```

#### Problem 3: Wspólna baza danych

```
┌─────────────────────────────────────────┐
│           WSPÓLNA BAZA                   │
│                                         │
│  Tabela users    ←─── Moduł A          │
│       ▲                                 │
│       │ Foreign Key                     │
│       ▼                                 │
│  Tabela orders   ←─── Moduł B          │
│       ▲                                 │
│       │ Foreign Key                     │
│       ▼                                 │
│  Tabela payments ←─── Moduł C          │
│                                         │
└─────────────────────────────────────────┘

Problem: Zmiana w "users" może zepsuć "orders" i "payments"
```

**To zobaczycie na labach!** Gdy jeden student zmieni schemat, inni mogą mieć problemy.

#### Problem 4: Zespoły nie mogą pracować niezależnie

```
Zespół A: "Chcemy zmienić tabelę users"
Zespół B: "Nie! Zepsujecie nam orders!"
Zespół C: "A my potrzebujemy nowego pola w users"

Rezultat: Spotkania, negocjacje, blokady
```

#### Problem 5: Technology lock-in

```
Monolit w PHP:
- Wszystko musi być w PHP
- Chcesz użyć Python ML? Osobny serwis.
- Chcesz użyć Go dla wydajności? Osobny serwis.

Efekt: Albo wszystko w jednej technologii, albo "organiczny" rozpad na serwisy
```

---

## Podsumowanie

### 9. Kiedy monolit, kiedy mikroserwisy? (~5 min)

| Sytuacja | Wybór |
|----------|-------|
| Startup, MVP, prototyp | **Monolit** |
| Mały zespół (< 10 osób) | **Monolit** |
| Prosta domena | **Monolit** |
| Jasne granice modułów | Można rozważyć mikroserwisy |
| Niezależne skalowanie | Mikroserwisy |
| Duże zespoły | Mikroserwisy |
| Netflix, Allegro | Mikroserwisy (ale zaczynali od monolitu!) |

**Złota zasada:**
> "Zacznij od monolitu. Wydzielaj serwisy gdy ból stanie się nie do zniesienia."
> — Martin Fowler (parafrazując)

### Co dalej na zajęciach

| Tydzień | Co robimy | Dlaczego |
|---------|-----------|----------|
| 3 (teraz) | Symfony CRUD (monolit) | Zrozumienie podstaw |
| 4 | CI/CD | Automatyzacja deploymentu |
| 5+ | Podział na serwisy | Gdy poczujecie ból monolitu |

**Na labach doświadczycie problemy monolitu:**
- Wspólna baza = konflikty
- Zmiany schematu = problemy dla innych
- Brak kontraktów = niespodzianki

To przygotuje was na rozwiązania w kolejnych tygodniach.

---

## Materiały dodatkowe

### Do poczytania
- [MonolithFirst - Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
- [The Majestic Monolith - DHH (Basecamp)](https://m.signalvnoise.com/the-majestic-monolith/)
- [Historia Facebooka - engineering blog](https://engineering.fb.com/)

### Do obejrzenia
- [Scaling Instagram Infrastructure (YouTube)](https://www.youtube.com/watch?v=hnpzNAPiC0E)

---

## Notatki prowadzącego

### Pytania które mogą paść
- "Czy PHP jest martwy?" → Nie. WordPress = 40% internetu. Laravel bardzo popularny.
- "Dlaczego nie zacząć od razu od mikroserwisów?" → Złożoność, koszt, nie znasz jeszcze granic domeny
- "Allegro nadal używa PHP?" → Już nie w głównych serwisach, ale migracja trwała lata

### Elementy interaktywne
- "Kto pisał kiedyś w PHP?"
- "Kto miał problem z SQL Injection?"
- Dyskusja: "Czy wasz projekt na studiach był monolitem?"

### Czas
- Całość: ~70 min
- Zostaje ~20 min na pytania i dyskusję
