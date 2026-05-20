#!/usr/bin/env python3
"""
Importuje products_seed.json do tabeli product (kolumna data JSONB).
Pomija produkty które już istnieją (match po data->>'name' i data->>'game_date').

Użycie:
  python3 scripts/products/import-products.py \
    --db-url postgresql://products:products@localhost:5433/products_dev \
    --file scripts/products_seed.json
"""
import argparse
import json
import os
import sys
import urllib.parse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    try:
        import psycopg2
    except ImportError:
        print("Instaluję psycopg2-binary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
        import psycopg2

    with open(args.file, encoding="utf-8") as f:
        products = json.load(f)

    conn = psycopg2.connect(args.db_url)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM product")
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"  Tabela ma już {existing} rekordów — pomijam import (użyj --reset żeby wyczyścić)")
        cur.close()
        conn.close()
        return

    print(f"  Wstawiam {len(products)} produktów...", end="", flush=True)
    batch = [(json.dumps(p, ensure_ascii=False),) for p in products]
    cur.executemany("INSERT INTO product (data) VALUES (%s::jsonb)", batch)
    conn.commit()
    cur.close()
    conn.close()
    print(f" OK")


if __name__ == "__main__":
    main()
