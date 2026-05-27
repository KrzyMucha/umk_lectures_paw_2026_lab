import os

import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

OLLAMA_MODEL = "nomic-embed-text"
GEMINI_MODEL = "text-embedding-004"


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
        json={"content": {"parts": [{"text": text}]}},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]


EMBEDDERS = {
    "ollama": embed_ollama,
    "gemini": embed_gemini,
}
