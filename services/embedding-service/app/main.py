import json
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.models import SearchRequest, SearchResponse, SearchResultItem
from app.qdrant import COLLECTION_NAME, MODELS, ensure_collection, get_client

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("embedding-service")


@asynccontextmanager
async def lifespan(a: FastAPI):
    ensure_collection()
    yield


app = FastAPI(title="Embedding Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    logger.info(json.dumps({"message": "health check", "status": "ok"}))
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    expected_dim = MODELS[req.model]

    if len(req.vector) != expected_dim:
        raise HTTPException(
            status_code=400,
            detail=f"Vector dimension mismatch: expected {expected_dim} for model '{req.model}', got {len(req.vector)}",
        )

    results_raw = get_client().query_points(
        collection_name=COLLECTION_NAME,
        query=req.vector,
        using=req.model,
        query_filter=Filter(
            must=[FieldCondition(key="model", match=MatchValue(value=req.model))]
        ),
        limit=req.limit,
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
        json.dumps({"message": "search", "model": req.model, "results": len(results)})
    )

    return SearchResponse(results=results, model=req.model, count=len(results))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
