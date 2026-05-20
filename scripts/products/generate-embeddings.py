#!/usr/bin/env python3
"""
Generuje embeddingi dla produktów przez lokalny Ollama (nomic-embed-text)
i zapisuje do tabeli product (kolumna embedding).

Użycie:
  python3 scripts/products/generate-embeddings.py \
    --db-url postgresql://products:products@localhost:5433/products_dev
"""
import argparse
import json
import sys
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list[float]:
    body = json.dumps({"model": MODEL, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["embedding"]


def price_label(price: float) -> str:
    if price < 40:
        return f"cheap budget affordable low price ${price:.2f}"
    elif price < 90:
        return f"affordable mid-range price ${price:.2f}"
    elif price < 180:
        return f"mid-range price ${price:.2f}"
    else:
        return f"expensive premium luxury high price ${price:.2f}"

def product_text(data: dict) -> str:
    """Łączy pola produktu w jeden tekst do embeddingu."""
    price = float(data.get("price", 0))
    pts   = data.get("points", 0)
    reb   = data.get("rebounds", 0)
    ast   = data.get("assists", 0)
    stl   = data.get("steals", 0)
    blk   = data.get("blocks", 0)
    parts = [
        data.get("name", ""),
        data.get("description", ""),
        price_label(price),
        f"player: {data.get('player', '')}",
        f"opponent: {data.get('opponent', '')}",
        f"game date: {data.get('game_date', '')}",
        f"{pts} points {reb} rebounds {ast} assists {stl} steals {blk} blocks",
    ]
    return " | ".join(p for p in parts if p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db-url",
        default="postgresql://products:products@localhost:5433/products_dev",
    )
    args = parser.parse_args()

    try:
        import psycopg2
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
        import psycopg2

    # sprawdź Ollama
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
    except Exception:
        print("BŁĄD: Ollama nie działa. Uruchom: brew services start ollama")
        sys.exit(1)

    conn = psycopg2.connect(args.db_url)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("SELECT id, data FROM product WHERE embedding IS NULL ORDER BY id")
    rows = cur.fetchall()
    total = len(rows)

    if total == 0:
        print("Wszystkie produkty mają już embeddingi.")
        cur.close()
        conn.close()
        return

    print(f"Generuję embeddingi dla {total} produktów...")

    for i, (product_id, data) in enumerate(rows, 1):
        text = product_text(data)
        try:
            embedding = get_embedding(text)
            vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
            cur.execute(
                "UPDATE product SET embedding = %s::vector WHERE id = %s",
                (vec_str, product_id),
            )
            if i % 50 == 0 or i == total:
                conn.commit()
                print(f"  {i}/{total} ({100*i//total}%)", flush=True)
        except Exception as e:
            print(f"  BŁĄD przy id={product_id}: {e}")
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nGotowe! Zindeksowano {total} produktów.")


if __name__ == "__main__":
    main()
