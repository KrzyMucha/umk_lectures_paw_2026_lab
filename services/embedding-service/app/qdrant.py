import logging
import os

from qdrant_client import QdrantClient

logger = logging.getLogger("embedding-service")

_client: QdrantClient | None = None

# Collection is managed externally (pre-populated `ai-arxiv`). The service
# never creates, deletes, or writes to it — it only issues read queries.
COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION", "ai-arxiv")


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        url = os.environ.get("QDRANT_URL", "http://localhost:6333")
        _client = QdrantClient(url=url)
    return _client


def verify_collection() -> None:
    """Read-only startup check. Logs a warning if the collection is missing;
    never creates or mutates it."""
    if not get_client().collection_exists(COLLECTION_NAME):
        logger.warning(
            "Qdrant collection %r not found — /search will fail until it exists",
            COLLECTION_NAME,
        )
