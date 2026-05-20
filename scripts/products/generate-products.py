#!/usr/bin/env python3
"""
Generuje 1000 produktów (ciuchy i buty legend koszykówki NBA) lokalnie — bez API.
Wynik: scripts/products_seed.json  i  scripts/products_seed.sql

Użycie:
  python3 scripts/generate-products.py
"""

import json
import os
import random

random.seed(42)

# ---------------------------------------------------------------------------
# Dane źródłowe
# ---------------------------------------------------------------------------

PLAYERS = [
    {
        "name": "Michael Jordan",
        "number": 23,
        "team": "Chicago Bulls",
        "games": [
            {"date": "1991-06-12", "opponent": "Los Angeles Lakers", "pts": 30, "reb": 10, "ast": 10, "stl": 2, "blk": 1},
            {"date": "1993-06-20", "opponent": "Phoenix Suns",       "pts": 55, "reb":  8, "ast":  4, "stl": 2, "blk": 1},
            {"date": "1996-06-16", "opponent": "Seattle SuperSonics", "pts": 22, "reb":  9, "ast":  7, "stl": 1, "blk": 0},
            {"date": "1997-06-11", "opponent": "Utah Jazz",           "pts": 38, "reb":  7, "ast":  5, "stl": 3, "blk": 0},
            {"date": "1998-06-14", "opponent": "Utah Jazz",           "pts": 45, "reb":  8, "ast":  3, "stl": 1, "blk": 0},
        ],
    },
    {
        "name": "Kobe Bryant",
        "number": 24,
        "team": "Los Angeles Lakers",
        "games": [
            {"date": "2000-06-19", "opponent": "Indiana Pacers",      "pts": 26, "reb":  6, "ast":  5, "stl": 2, "blk": 1},
            {"date": "2006-01-22", "opponent": "Toronto Raptors",     "pts": 81, "reb":  6, "ast":  2, "stl": 2, "blk": 1},
            {"date": "2009-06-14", "opponent": "Orlando Magic",       "pts": 30, "reb":  6, "ast":  8, "stl": 1, "blk": 0},
            {"date": "2010-06-17", "opponent": "Boston Celtics",      "pts": 23, "reb": 15, "ast":  4, "stl": 1, "blk": 2},
            {"date": "2016-04-13", "opponent": "Utah Jazz",           "pts": 60, "reb":  4, "ast":  4, "stl": 1, "blk": 0},
        ],
    },
    {
        "name": "LeBron James",
        "number": 23,
        "team": "Cleveland Cavaliers",
        "games": [
            {"date": "2016-06-19", "opponent": "Golden State Warriors","pts": 27, "reb": 11, "ast": 11, "stl": 3, "blk": 3},
            {"date": "2012-06-21", "opponent": "Oklahoma City Thunder","pts": 26, "reb": 11, "ast": 13, "stl": 3, "blk": 0},
            {"date": "2020-10-11", "opponent": "Miami Heat",           "pts": 28, "reb": 14, "ast": 10, "stl": 1, "blk": 0},
            {"date": "2018-06-03", "opponent": "Golden State Warriors","pts": 51, "reb":  8, "ast":  8, "stl": 1, "blk": 0},
            {"date": "2023-02-07", "opponent": "Oklahoma City Thunder","pts": 38, "reb":  8, "ast": 12, "stl": 2, "blk": 1},
        ],
    },
    {
        "name": "Magic Johnson",
        "number": 32,
        "team": "Los Angeles Lakers",
        "games": [
            {"date": "1980-05-16", "opponent": "Philadelphia 76ers",  "pts": 42, "reb": 15, "ast":  7, "stl": 3, "blk": 1},
            {"date": "1987-06-14", "opponent": "Boston Celtics",      "pts": 29, "reb": 11, "ast": 10, "stl": 2, "blk": 0},
            {"date": "1988-06-21", "opponent": "Detroit Pistons",     "pts": 22, "reb":  8, "ast": 12, "stl": 1, "blk": 0},
            {"date": "1991-06-09", "opponent": "Chicago Bulls",       "pts": 19, "reb":  7, "ast": 11, "stl": 2, "blk": 0},
            {"date": "1992-02-09", "opponent": "All-Star Game",       "pts": 25, "reb":  5, "ast":  9, "stl": 2, "blk": 0},
        ],
    },
    {
        "name": "Larry Bird",
        "number": 33,
        "team": "Boston Celtics",
        "games": [
            {"date": "1984-06-12", "opponent": "Los Angeles Lakers",  "pts": 29, "reb": 15, "ast": 12, "stl": 2, "blk": 1},
            {"date": "1986-06-08", "opponent": "Houston Rockets",     "pts": 29, "reb": 11, "ast":  7, "stl": 2, "blk": 0},
            {"date": "1987-05-26", "opponent": "Detroit Pistons",     "pts": 37, "reb":  9, "ast":  9, "stl": 5, "blk": 0},
            {"date": "1988-06-10", "opponent": "Los Angeles Lakers",  "pts": 28, "reb": 10, "ast":  8, "stl": 1, "blk": 1},
            {"date": "1991-01-27", "opponent": "Portland Trail Blazers","pts": 49,"reb": 14, "ast": 12, "stl": 1, "blk": 0},
        ],
    },
    {
        "name": "Shaquille O'Neal",
        "number": 34,
        "team": "Los Angeles Lakers",
        "games": [
            {"date": "2000-06-19", "opponent": "Indiana Pacers",      "pts": 41, "reb": 12, "ast":  4, "stl": 0, "blk": 2},
            {"date": "2001-06-15", "opponent": "Philadelphia 76ers",  "pts": 29, "reb": 17, "ast":  4, "stl": 0, "blk": 4},
            {"date": "2002-06-12", "opponent": "New Jersey Nets",     "pts": 36, "reb": 12, "ast":  2, "stl": 1, "blk": 3},
            {"date": "2006-06-20", "opponent": "Dallas Mavericks",    "pts": 28, "reb": 11, "ast":  2, "stl": 0, "blk": 2},
            {"date": "1994-04-24", "opponent": "New Jersey Nets",     "pts": 53, "reb": 12, "ast":  5, "stl": 1, "blk": 4},
        ],
    },
    {
        "name": "Kareem Abdul-Jabbar",
        "number": 33,
        "team": "Los Angeles Lakers",
        "games": [
            {"date": "1985-06-09", "opponent": "Boston Celtics",      "pts": 30, "reb": 17, "ast":  8, "stl": 1, "blk": 3},
            {"date": "1980-05-16", "opponent": "Philadelphia 76ers",  "pts": 40, "reb": 15, "ast":  4, "stl": 1, "blk": 2},
            {"date": "1974-05-12", "opponent": "Boston Celtics",      "pts": 35, "reb": 16, "ast":  3, "stl": 1, "blk": 5},
            {"date": "1971-04-30", "opponent": "Baltimore Bullets",   "pts": 27, "reb": 16, "ast":  3, "stl": 0, "blk": 4},
            {"date": "1988-06-07", "opponent": "Detroit Pistons",     "pts": 32, "reb": 13, "ast":  5, "stl": 0, "blk": 3},
        ],
    },
    {
        "name": "Allen Iverson",
        "number": 3,
        "team": "Philadelphia 76ers",
        "games": [
            {"date": "2001-06-06", "opponent": "Los Angeles Lakers",  "pts": 48, "reb":  6, "ast":  5, "stl": 3, "blk": 1},
            {"date": "2005-12-10", "opponent": "Cleveland Cavaliers", "pts": 54, "reb":  7, "ast":  4, "stl": 4, "blk": 0},
            {"date": "2000-02-24", "opponent": "Chicago Bulls",       "pts": 50, "reb":  5, "ast":  4, "stl": 5, "blk": 0},
            {"date": "2003-03-12", "opponent": "Miami Heat",          "pts": 55, "reb":  6, "ast":  5, "stl": 4, "blk": 0},
            {"date": "1999-02-06", "opponent": "New York Knicks",     "pts": 41, "reb":  5, "ast":  7, "stl": 3, "blk": 0},
        ],
    },
    {
        "name": "Kevin Durant",
        "number": 35,
        "team": "Oklahoma City Thunder",
        "games": [
            {"date": "2012-06-21", "opponent": "Miami Heat",          "pts": 32, "reb": 11, "ast":  5, "stl": 1, "blk": 1},
            {"date": "2017-06-12", "opponent": "Cleveland Cavaliers", "pts": 39, "reb":  8, "ast":  5, "stl": 1, "blk": 3},
            {"date": "2021-06-19", "opponent": "Milwaukee Bucks",     "pts": 32, "reb": 11, "ast":  4, "stl": 1, "blk": 2},
            {"date": "2014-05-08", "opponent": "Los Angeles Clippers","pts": 36, "reb":  9, "ast":  5, "stl": 1, "blk": 0},
            {"date": "2013-04-27", "opponent": "Houston Rockets",     "pts": 42, "reb": 12, "ast":  8, "stl": 2, "blk": 0},
        ],
    },
    {
        "name": "Stephen Curry",
        "number": 30,
        "team": "Golden State Warriors",
        "games": [
            {"date": "2015-06-16", "opponent": "Cleveland Cavaliers", "pts": 38, "reb":  6, "ast":  6, "stl": 2, "blk": 0},
            {"date": "2018-06-08", "opponent": "Cleveland Cavaliers", "pts": 37, "reb":  7, "ast":  7, "stl": 1, "blk": 0},
            {"date": "2016-02-27", "opponent": "Oklahoma City Thunder","pts": 46, "reb":  3, "ast":  8, "stl": 3, "blk": 0},
            {"date": "2021-04-12", "opponent": "Denver Nuggets",      "pts": 53, "reb":  7, "ast":  6, "stl": 2, "blk": 0},
            {"date": "2022-06-16", "opponent": "Boston Celtics",      "pts": 34, "reb":  7, "ast":  7, "stl": 2, "blk": 0},
        ],
    },
    {
        "name": "Tim Duncan",
        "number": 21,
        "team": "San Antonio Spurs",
        "games": [
            {"date": "2003-06-15", "opponent": "New Jersey Nets",     "pts": 21, "reb": 20, "ast": 10, "stl": 1, "blk": 8},
            {"date": "2005-06-23", "opponent": "Detroit Pistons",     "pts": 25, "reb": 11, "ast":  7, "stl": 1, "blk": 2},
            {"date": "2007-06-14", "opponent": "Cleveland Cavaliers", "pts": 24, "reb": 17, "ast":  4, "stl": 1, "blk": 3},
            {"date": "2014-06-15", "opponent": "Miami Heat",          "pts": 13, "reb": 10, "ast":  4, "stl": 1, "blk": 2},
            {"date": "1999-06-25", "opponent": "New York Knicks",     "pts": 33, "reb": 16, "ast":  4, "stl": 0, "blk": 2},
        ],
    },
    {
        "name": "Charles Barkley",
        "number": 34,
        "team": "Phoenix Suns",
        "games": [
            {"date": "1993-06-20", "opponent": "Chicago Bulls",       "pts": 24, "reb": 19, "ast":  6, "stl": 1, "blk": 0},
            {"date": "1993-06-16", "opponent": "Chicago Bulls",       "pts": 42, "reb": 13, "ast":  5, "stl": 2, "blk": 0},
            {"date": "1992-02-09", "opponent": "All-Star Game",       "pts": 17, "reb": 22, "ast":  7, "stl": 2, "blk": 0},
            {"date": "1988-05-20", "opponent": "Boston Celtics",      "pts": 30, "reb": 18, "ast":  4, "stl": 2, "blk": 0},
            {"date": "1995-05-14", "opponent": "Houston Rockets",     "pts": 35, "reb": 14, "ast":  6, "stl": 1, "blk": 0},
        ],
    },
    {
        "name": "Scottie Pippen",
        "number": 33,
        "team": "Chicago Bulls",
        "games": [
            {"date": "1994-05-13", "opponent": "New York Knicks",     "pts": 25, "reb": 12, "ast":  8, "stl": 4, "blk": 2},
            {"date": "1996-06-16", "opponent": "Seattle SuperSonics", "pts": 20, "reb": 10, "ast":  7, "stl": 3, "blk": 2},
            {"date": "1992-06-14", "opponent": "Portland Trail Blazers","pts":26, "reb":  8, "ast":  8, "stl": 5, "blk": 0},
            {"date": "1998-06-14", "opponent": "Utah Jazz",           "pts": 23, "reb":  8, "ast":  7, "stl": 3, "blk": 2},
            {"date": "1991-06-12", "opponent": "Los Angeles Lakers",  "pts": 20, "reb":  9, "ast": 10, "stl": 3, "blk": 1},
        ],
    },
    {
        "name": "Hakeem Olajuwon",
        "number": 34,
        "team": "Houston Rockets",
        "games": [
            {"date": "1994-06-22", "opponent": "New York Knicks",     "pts": 25, "reb": 10, "ast":  7, "stl": 2, "blk": 6},
            {"date": "1995-06-14", "opponent": "Orlando Magic",       "pts": 35, "reb": 15, "ast":  5, "stl": 2, "blk": 4},
            {"date": "1994-06-17", "opponent": "New York Knicks",     "pts": 37, "reb":  9, "ast":  5, "stl": 3, "blk": 4},
            {"date": "1996-05-06", "opponent": "Seattle SuperSonics", "pts": 39, "reb": 11, "ast":  7, "stl": 2, "blk": 5},
            {"date": "1993-05-18", "opponent": "Seattle SuperSonics", "pts": 43, "reb": 18, "ast":  4, "stl": 3, "blk": 6},
        ],
    },
    {
        "name": "Dennis Rodman",
        "number": 91,
        "team": "Chicago Bulls",
        "games": [
            {"date": "1996-06-16", "opponent": "Seattle SuperSonics", "pts":  8, "reb": 19, "ast":  2, "stl": 2, "blk": 1},
            {"date": "1992-06-14", "opponent": "Portland Trail Blazers","pts":10, "reb": 21, "ast":  3, "stl": 1, "blk": 0},
            {"date": "1998-06-14", "opponent": "Utah Jazz",           "pts":  9, "reb": 18, "ast":  2, "stl": 2, "blk": 1},
            {"date": "1990-06-05", "opponent": "Portland Trail Blazers","pts":11, "reb": 17, "ast":  2, "stl": 1, "blk": 0},
            {"date": "1997-06-11", "opponent": "Utah Jazz",           "pts":  6, "reb": 13, "ast":  3, "stl": 0, "blk": 0},
        ],
    },
]

PRODUCT_TYPES = [
    ("Jersey", "Authentic replica jersey", 119.99, 169.99),
    ("Shorts", "Game-day shorts", 69.99, 99.99),
    ("Hoodie", "Premium pullover hoodie", 89.99, 139.99),
    ("Jacket", "Warm-up jacket", 129.99, 199.99),
    ("Snapback Cap", "Adjustable snapback cap", 34.99, 49.99),
    ("Crew Socks", "Cushioned crew socks", 19.99, 29.99),
    ("Signature Shoes", "Signature basketball shoes", 149.99, 299.99),
    ("Gym Bag", "Team gym bag", 59.99, 89.99),
    ("Tracksuit", "Full tracksuit set", 179.99, 249.99),
    ("T-Shirt", "Casual graphic tee", 29.99, 49.99),
]

EDITIONS = [
    "Retro", "Limited Edition", "Championship", "All-Star", "Hardwood Classics",
    "City Edition", "Statement Edition", "Icon Edition", "Classic Edition", "Throwback",
]


# ---------------------------------------------------------------------------
# Generowanie
# ---------------------------------------------------------------------------

def generate_products(total: int = 1000) -> list:
    products = []
    per_player = total // len(PLAYERS)
    per_type = per_player // len(PRODUCT_TYPES)

    for player in PLAYERS:
        game_cycle = player["games"] * (per_player // len(player["games"]) + 1)
        game_idx = 0
        for ptype, base_desc, price_lo, price_hi in PRODUCT_TYPES:
            for edition_idx in range(max(per_type, 1)):
                edition = EDITIONS[edition_idx % len(EDITIONS)]
                game = game_cycle[game_idx % len(game_cycle)]
                game_idx += 1
                price = round(random.uniform(price_lo, price_hi), 2)
                name = f"{player['name']} #{player['number']} {edition} {ptype}"[:80]
                description = (
                    f"{edition} {ptype} inspired by {player['name']}. "
                    f"Worn vs {game['opponent']} on {game['date']}."
                )[:200]
                products.append({
                    "name": name,
                    "description": description,
                    "price": price,
                    "player": player["name"],
                    "game_date": game["date"],
                    "opponent": game["opponent"],
                    "points": game["pts"],
                    "rebounds": game["reb"],
                    "assists": game["ast"],
                    "steals": game["stl"],
                    "blocks": game["blk"],
                })

    # uzupełnij do dokładnie 1000 losowymi kombinacjami
    while len(products) < total:
        player = random.choice(PLAYERS)
        game = random.choice(player["games"])
        ptype, base_desc, price_lo, price_hi = random.choice(PRODUCT_TYPES)
        edition = random.choice(EDITIONS)
        price = round(random.uniform(price_lo, price_hi), 2)
        name = f"{player['name']} #{player['number']} {edition} {ptype}"[:80]
        description = (
            f"{edition} {ptype} inspired by {player['name']}. "
            f"Worn vs {game['opponent']} on {game['date']}."
        )[:200]
        products.append({
            "name": name,
            "description": description,
            "price": price,
            "player": player["name"],
            "game_date": game["date"],
            "opponent": game["opponent"],
            "points": game["pts"],
            "rebounds": game["reb"],
            "assists": game["ast"],
            "steals": game["stl"],
            "blocks": game["blk"],
        })

    return products[:total]


def escape_sql(s: str) -> str:
    return s.replace("'", "''")


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("Generuję 1000 produktów lokalnie...")
    products = generate_products(1000)

    # JSON
    json_path = os.path.join(out_dir, "products_seed.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"Zapisano JSON:  {json_path}")

    # SQL
    sql_path = os.path.join(out_dir, "products_seed.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- Wygenerowane lokalnie przez generate-products.py\n")
        f.write("-- Kategoria: ciuchy i buty legend koszykówki NBA\n\n")
        f.write("TRUNCATE TABLE product RESTART IDENTITY CASCADE;\n\n")
        f.write("INSERT INTO product (name, description, price, player, game_date, opponent, points, rebounds, assists, steals, blocks) VALUES\n")
        rows = []
        for p in products:
            rows.append(
                f"  ('{escape_sql(p['name'])}', '{escape_sql(p['description'])}', "
                f"{p['price']:.2f}, '{escape_sql(p['player'])}', '{p['game_date']}', "
                f"'{escape_sql(p['opponent'])}', {p['points']}, {p['rebounds']}, "
                f"{p['assists']}, {p['steals']}, {p['blocks']})"
            )
        f.write(",\n".join(rows))
        f.write(";\n")
    print(f"Zapisano SQL:   {sql_path}")
    print(f"\nGotowe! {len(products)} produktów.")


if __name__ == "__main__":
    main()



def call_gemini(prompt: str) -> str:
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 8192}
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 15 * (attempt + 1)
                print(f"  429 Too Many Requests — czekam {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Przekroczono limit prób (429)")


def build_prompt(batch_num: int, count: int) -> str:
    legends_str = ", ".join(LEGENDS)
    return f"""Wygeneruj listę {count} unikalnych produktów ze sklepu sportowego inspirowanych legendami koszykówki NBA.
Legendy: {legends_str}.

Produkty to: koszulki, spodenki, bluzy, kurtki, czapki, skarpety, buty, torby — inspirowane stylem i numerami tych graczy.
Każdy produkt powinien mieć inną legendę jako inspirację (rozłóż równomiernie).
Batch numer {batch_num} — produkty muszą być INNE niż w poprzednich batchach, wymyślaj nowe warianty.

Dla każdego produktu podaj też informacje o konkretnym meczu NBA w którym dany zawodnik użył tego stroju/butów,
oraz statystyki zawodnika z tego meczu.

Odpowiedz WYŁĄCZNIE poprawnym JSON w formacie:
[
  {{
    "name": "...",
    "description": "...",
    "price": 99.99,
    "player": "Michael Jordan",
    "game_date": "1991-06-12",
    "opponent": "Los Angeles Lakers",
    "points": 30,
    "rebounds": 7,
    "assists": 10,
    "steals": 2,
    "blocks": 1
  }},
  ...
]

Zasady:
- name: krótka nazwa produktu po angielsku (maks. 80 znaków)
- description: 1-2 zdania po angielsku opisujące produkt i jego związek z meczem (maks. 200 znaków)
- price: liczba od 29.99 do 499.99
- player: imię i nazwisko legendy z podanej listy
- game_date: data w formacie YYYY-MM-DD, realistyczna dla kariery danego zawodnika
- opponent: nazwa drużyny przeciwnej (prawdziwa drużyna NBA)
- points, rebounds, assists, steals, blocks: liczby całkowite, realistyczne dla danego zawodnika
- Nie dodawaj żadnego tekstu poza JSON
"""


def escape_sql(s: str) -> str:
    return s.replace("'", "''")


def extract_json(text: str) -> list:
    text = text.strip()
    # usuń markdown code block jeśli Gemini go doda
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)


def main():
    all_products = []
    batches = TOTAL // BATCH_SIZE
    progress_path = os.path.join(os.path.dirname(__file__), "products_progress.json")

    # wznów od poprzedniego postępu jeśli istnieje
    if os.path.exists(progress_path):
        with open(progress_path, "r", encoding="utf-8") as f:
            all_products = json.load(f)
        print(f"Wznawianie — załadowano {len(all_products)} produktów z poprzedniego uruchomienia")

    start_batch = len(all_products) // BATCH_SIZE

    for i in range(start_batch, batches):
        batch_num = i + 1
        print(f"Generuję batch {batch_num}/{batches} ({BATCH_SIZE} produktów)...", flush=True)
        try:
            raw = call_gemini(build_prompt(batch_num, BATCH_SIZE))
            products = extract_json(raw)
            all_products.extend(products)
            # zapisz postęp po każdym batchu
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(all_products, f, ensure_ascii=False)
            print(f"  OK — łącznie {len(all_products)} produktów")
            if i < batches - 1:
                time.sleep(6)  # ~10 req/min, bezpiecznie poniżej limitu 15 req/min
        except Exception as e:
            print(f"  BŁĄD w batch {batch_num}: {e}")
            print(f"  Postęp zapisany ({len(all_products)} produktów) — uruchom ponownie żeby kontynuować")
            sys.exit(1)
    output_path = os.path.join(os.path.dirname(__file__), "products_seed.sql")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("-- Wygenerowane automatycznie przez generate-products.py\n")
        f.write("-- Kategoria: ciuchy i buty legend koszykówki NBA\n\n")
        f.write("TRUNCATE TABLE product RESTART IDENTITY CASCADE;\n\n")
        f.write("INSERT INTO product (name, description, price, player, game_date, opponent, points, rebounds, assists, steals, blocks) VALUES\n")

        rows = []
        for p in all_products:
            name     = escape_sql(str(p.get("name", ""))[:80])
            desc     = escape_sql(str(p.get("description", ""))[:200])
            price    = float(p.get("price", 49.99))
            player   = escape_sql(str(p.get("player", ""))[:100])
            game_date = escape_sql(str(p.get("game_date", "2000-01-01")))
            opponent = escape_sql(str(p.get("opponent", ""))[:100])
            pts      = int(p.get("points", 0))
            reb      = int(p.get("rebounds", 0))
            ast      = int(p.get("assists", 0))
            stl      = int(p.get("steals", 0))
            blk      = int(p.get("blocks", 0))
            rows.append(
                f"  ('{name}', '{desc}', {price:.2f}, '{player}', '{game_date}', '{opponent}', {pts}, {reb}, {ast}, {stl}, {blk})"
            )

        f.write(",\n".join(rows))
        f.write(";\n")

    print(f"\nGotowe! Zapisano {len(all_products)} produktów do: {output_path}")
    print(f"Importuj: psql $DATABASE_URL -f scripts/products_seed.sql")


if __name__ == "__main__":
    main()
