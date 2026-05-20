#!/usr/bin/env python3
"""
Generuje opisy produktów przez Groq API i zapisuje do products_seed.json.
Wznawia od miejsca przerwania.

Użycie:
  export GROQ_API_KEY=twój_klucz
  python3 scripts/generate-descriptions.py
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Błąd: ustaw zmienną GROQ_API_KEY")
    sys.exit(1)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"
BATCH_SIZE = 5

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "products_seed.json")


def call_groq(prompt: str) -> str:
    for attempt in range(6):
        body_data = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.8,
        }).encode("utf-8")
        attempt_req = urllib.request.Request(
            GROQ_URL,
            data=body_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": "python-requests/2.31.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(attempt_req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 15 * (attempt + 1)
                print(f"  429 — czekam {wait}s...", flush=True)
                time.sleep(wait)
            elif e.code == 401:
                wait = 60 * (attempt + 1)
                print(f"  401 (limit?) — czekam {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Przekroczono limit prób")


def build_batch_prompt(batch: list) -> str:
    lines = [
        "You are a passionate NBA merchandise copywriter. Write vivid, imaginative product descriptions.",
        "For each item below, write TWO paragraphs:",
        "- Paragraph 1: describe the garment (fabric, fit, design details, colors) in an exciting, collector-worthy way.",
        "- Paragraph 2: paint a dramatic scene from that specific game — invent crowd atmosphere, key moments, legendary plays that happened during those stats. Make it feel like the fan was there.",
        "Each description should be 60-100 words total.",
        "IMPORTANT: Separate descriptions with exactly this delimiter on its own line: |||",
        "Do NOT use ||| inside a description. No numbering, no intro text.\n",
    ]
    for i, p in enumerate(batch):
        lines.append(
            f"{i+1}. {p['name']} | Player: {p['player']} | "
            f"Game: vs {p['opponent']} on {p['game_date']} | "
            f"Stats: {p['points']}pts {p['rebounds']}reb {p['assists']}ast {p['steals']}stl {p['blocks']}blk"
        )
    return "\n".join(lines)


def parse_batch_response(text: str, expected: int) -> list:
    parts = [p.strip() for p in text.split("|||")]
    parts = [p for p in parts if p]  # usuń puste
    if len(parts) != expected:
        print(f"  UWAGA: oczekiwano {expected} opisów, dostałem {len(parts)} — zapisuję częściowe")
    return parts


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    # zbierz indeksy produktów które potrzebują opisu
    to_update = [
        i for i, p in enumerate(products)
        if "Worn vs" in p.get("description", "") or len(p.get("description", "")) < 100
    ]
    total_batches = (len(to_update) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Produktów do opisania: {len(to_update)}, batchów: {total_batches}")

    for b, batch_start in enumerate(range(0, len(to_update), BATCH_SIZE)):
        batch_indices = to_update[batch_start:batch_start + BATCH_SIZE]
        batch = [products[i] for i in batch_indices]
        print(f"[{b+1}/{total_batches}] batch {batch_start+1}-{batch_start+len(batch)}...", flush=True)

        try:
            raw = call_groq(build_batch_prompt(batch))
            descriptions = parse_batch_response(raw, len(batch))
            # zapisz tyle ile dostaliśmy (może być mniej niż batch)
            for idx, desc in zip(batch_indices, descriptions):
                products[idx]["description"] = desc.strip()[:1000]

            # zapis po każdym batchu
            with open(INPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"  OK — zapisano {len(descriptions)}/{len(batch)}")
            time.sleep(2)  # 30 req/min limit

        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                print(f"  BŁĄD HTTP {e.code} — czekam 30s i próbuję dalej...")
                time.sleep(30)
                continue
            print(f"  BŁĄD HTTP {e.code}: {e.read().decode()[:200]}")
            with open(INPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            sys.exit(1)
        except Exception as e:
            print(f"  BŁĄD: {e} — pomijam batch, kontynuuję")
            with open(INPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            time.sleep(2)
            continue

    print(f"\nGotowe! Zaktualizowano opisy w {INPUT_FILE}")


if __name__ == "__main__":
    main()
