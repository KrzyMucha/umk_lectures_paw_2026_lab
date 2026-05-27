#!/usr/bin/env python3
"""Seed the Qdrant embeddings collection with test data (random vectors)."""
import os
import random

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")

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

    point_id = 1
    for model_name, dim in MODELS.items():
        points = [
            PointStruct(
                id=point_id + i,
                vector={model_name: random_vector(dim)},
                payload={"raw": text, "model": model_name},
            )
            for i, text in enumerate(SAMPLE_TEXTS)
        ]
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Seeded {len(points)} points for model '{model_name}'.")
        point_id += len(SAMPLE_TEXTS)


if __name__ == "__main__":
    main()
