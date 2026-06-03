#!/usr/bin/env python3
"""Seed a *local* Qdrant collection with test data.

Each point carries both named vectors (matching the live `ai-arxiv` schema)
and a `{raw}` payload. This is a local-dev convenience only — it refuses to
write to a collection that already contains points unless `--force` is passed,
so it can never clobber the populated production collection.
"""
import os
import random
import sys

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION", "ai-arxiv")

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "nomic-embed-text")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-embedding-001")
GEMINI_DIM = int(os.environ.get("GEMINI_DIM", "3072"))

# Qdrant named vector -> dimension. Must match the live `ai-arxiv` schema.
VECTORS = {
    "nomic-embed-text": 768,
    "gemini-embedding-2": GEMINI_DIM,
}

SAMPLE_TEXTS = [
    "Wireless Mouse - compact ergonomic design",
    "Mechanical Keyboard - Cherry MX switches",
    "USB-C Hub - 7 port multifunction adapter",
    "Monitor Stand - adjustable height bamboo",
    "Desk Lamp - LED with dimmer control",
    "Webcam HD - 1080p autofocus with mic",
    "Notebook A5 - dotted grid 200 pages",
    "Pen Set - gel ink assorted colors",
    "Backpack - water resistant laptop compartment",
    "Water Bottle - insulated stainless steel 750ml",
]


def embed_ollama(text: str) -> list[float]:
    resp = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": OLLAMA_MODEL, "input": text},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def embed_gemini(text: str) -> list[float]:
    resp = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:embedContent",
        params={"key": GEMINI_API_KEY},
        json={
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": GEMINI_DIM,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]


def random_vector(dim: int) -> list[float]:
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]


def main():
    force = "--force" in sys.argv
    client = QdrantClient(url=QDRANT_URL)

    # Safety guard: never overwrite a populated collection by accident.
    if client.collection_exists(COLLECTION_NAME):
        count = client.count(collection_name=COLLECTION_NAME).count
        if count > 0 and not force:
            print(
                f"Refusing to seed: collection {COLLECTION_NAME!r} already has "
                f"{count} points. Pass --force to overwrite (LOCAL ONLY).",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                name: VectorParams(size=size, distance=Distance.COSINE)
                for name, size in VECTORS.items()
            },
        )
    except UnexpectedResponse as e:
        if e.status_code != 409:
            raise

    ollama_available = False
    try:
        httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5.0).raise_for_status()
        ollama_available = True
        print("Ollama is available — using real nomic-embed-text embeddings.")
    except Exception:
        print("Ollama not available — using random vectors for nomic-embed-text.")

    gemini_available = bool(GEMINI_API_KEY)
    print(
        "Gemini API key set — using real embeddings."
        if gemini_available
        else "No GEMINI_API_KEY — using random vectors for gemini-embedding-2."
    )

    points = []
    for i, text in enumerate(SAMPLE_TEXTS):
        nomic_vec = embed_ollama(text) if ollama_available else random_vector(768)
        gemini_vec = embed_gemini(text) if gemini_available else random_vector(GEMINI_DIM)

        points.append(
            PointStruct(
                id=i + 1,
                vector={
                    "nomic-embed-text": nomic_vec,
                    "gemini-embedding-2": gemini_vec,
                },
                payload={"raw": text},
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Seeded {len(points)} points into {COLLECTION_NAME!r}.")


if __name__ == "__main__":
    main()
