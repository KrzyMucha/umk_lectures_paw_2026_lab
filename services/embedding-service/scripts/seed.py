#!/usr/bin/env python3
"""Seed the Qdrant embeddings collection with test data."""
import os
import random

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

COLLECTION_NAME = "embeddings"

MODELS = {
    "ollama": 768,
    "gemini": 768,
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
        json={"model": "nomic-embed-text", "input": text},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def random_vector(dim: int) -> list[float]:
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]


def main():
    client = QdrantClient(url=QDRANT_URL)

    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                name: VectorParams(size=size, distance=Distance.COSINE)
                for name, size in MODELS.items()
            },
        )
    except UnexpectedResponse as e:
        if e.status_code != 409:
            raise

    ollama_available = False
    try:
        httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5.0).raise_for_status()
        ollama_available = True
        print("Ollama is available — using real embeddings.")
    except Exception:
        print("Ollama not available — using random vectors.")

    points = []
    for i, text in enumerate(SAMPLE_TEXTS):
        if ollama_available:
            vec = embed_ollama(text)
        else:
            vec = random_vector(768)

        points.append(
            PointStruct(
                id=i + 1,
                vector={"ollama": vec},
                payload={"raw": text, "model": "ollama"},
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Seeded {len(points)} points for model 'ollama'.")


if __name__ == "__main__":
    main()
