#!/usr/bin/env python3
"""
Generuje embeddingi dla produktów przez Gemini API (gemini-embedding-001, 768-dim)
i zapisuje do tabeli product (kolumna embedding_gemini).

Użycie:
  python3 scripts/products/generate-embeddings-gemini.py \
    --db-url postgresql://products:products@localhost:5433/products_dev \
    --api-key AIza...

Lub ustaw GEMINI_API_KEY w .env / zmiennych środowiskowych.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
OUTPUT_DIM = 768


def get_embedding(text: str, api_key: str) -> list[float]:
    body = json.dumps({
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": OUTPUT_DIM,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["embedding"]["values"]


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


def load_env(path=".env"):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env("services/products-service/.env")

    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", default="postgresql://products:products@localhost:5433/products_dev")
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY", ""))
    args = parser.parse_args()

    if not args.api_key:
        print("BŁĄD: brak GEMINI_API_KEY. Ustaw w .env lub --api-key")
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
        import psycopg2

    conn = psycopg2.connect(args.db_url)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("SELECT id, data FROM product WHERE embedding_gemini IS NULL ORDER BY id")
    rows = cur.fetchall()
    total = len(rows)

    if total == 0:
        print("Wszystkie produkty mają już embeddingi Gemini.")
        cur.close(); conn.close(); return

    print(f"Generuję embeddingi Gemini dla {total} produktów (100 req/min limit)...")

    errors = 0
    for i, (product_id, data) in enumerate(rows, 1):
        text = product_text(data)
        try:
            embedding = get_embedding(text, args.api_key)
            vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
            cur.execute(
                "UPDATE product SET embedding_gemini = %s::vector WHERE id = %s",
                (vec_str, product_id),
            )
            if i % 50 == 0 or i == total:
                conn.commit()
                print(f"  {i}/{total} ({100*i//total}%)", flush=True)
            # ~100 req/min free tier → 0.65s przerwa
            time.sleep(0.65)
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429:
                print(f"  Rate limit przy id={product_id}, czekam 60s...")
                time.sleep(60)
                continue
            print(f"  BŁĄD HTTP {e.code} przy id={product_id}: {body[:200]}")
            errors += 1
            conn.rollback()
        except Exception as e:
            print(f"  BŁĄD przy id={product_id}: {e}")
            errors += 1
            conn.rollback()

    conn.commit()
    cur.close(); conn.close()
    print(f"\nGotowe! Zindeksowano {total - errors}/{total} produktów.")


if __name__ == "__main__":
    main()
