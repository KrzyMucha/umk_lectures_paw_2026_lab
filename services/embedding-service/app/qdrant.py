import os

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

_client: QdrantClient | None = None

COLLECTION_NAME = "embeddings"

MODELS = {
    "ollama": 768,
    "gemini": 768,
}


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        url = os.environ.get("QDRANT_URL", "http://localhost:6333")
        _client = QdrantClient(url=url)
    return _client


def ensure_collection():
    client = get_client()
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
