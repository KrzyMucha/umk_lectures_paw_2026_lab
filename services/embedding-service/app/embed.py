import os

import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "nomic-embed-text")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-embedding-001")
GEMINI_DIM = int(os.environ.get("GEMINI_DIM", "3072"))


def embed_ollama(text: str) -> list[float]:
    resp = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": OLLAMA_MODEL, "input": text},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def embed_gemini(text: str) -> list[float]:
    # Key goes in a header, never the URL/query string — otherwise it leaks into
    # httpx error messages, logs, and any echoed exception detail.
    resp = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:embedContent",
        headers={"x-goog-api-key": GEMINI_API_KEY},
        json={
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": GEMINI_DIM,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]


# API alias -> Qdrant named vector, its dimension, and the embedding function.
# The vector names match the live `ai-arxiv` collection schema.
MODELS = {
    "ollama": {"vector": "nomic-embed-text", "dim": 768, "embed": embed_ollama},
    "gemini": {"vector": "gemini-embedding-2", "dim": GEMINI_DIM, "embed": embed_gemini},
}
