import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Query

from app.embed import MODELS
from app.models import SearchResponse, SearchResultItem
from app.qdrant import COLLECTION_NAME, get_client, verify_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("embedding-service")


@asynccontextmanager
async def lifespan(a: FastAPI):
    verify_collection()
    yield


app = FastAPI(title="Embedding Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    logger.info(json.dumps({"message": "health check", "status": "ok"}))
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
def search(
    query: str = Query(min_length=1),
    model: Literal["ollama", "gemini"] = Query(),
    limit: int = Query(default=5, ge=1, le=100),
):
    cfg = MODELS.get(model)
    if cfg is None:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model}")

    try:
        vector = cfg["embed"](query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embedding failed: {e}")

    # Each point holds both named vectors; selecting the vector is enough — no
    # payload filtering needed.
    results_raw = get_client().query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        using=cfg["vector"],
        limit=limit,
        with_payload=True,
    )

    results = [
        SearchResultItem(
            id=point.id,
            raw=point.payload.get("raw", ""),
            score=point.score,
        )
        for point in results_raw.points
    ]

    logger.info(
        json.dumps({"message": "search", "model": model, "query": query, "results": len(results)})
    )

    return SearchResponse(results=results, model=model, count=len(results))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
