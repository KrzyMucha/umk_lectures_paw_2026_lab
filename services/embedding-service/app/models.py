from typing import Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    vector: list[float]
    model: Literal["ollama", "gemini"]
    limit: int = Field(default=5, ge=1, le=100)


class SearchResultItem(BaseModel):
    id: int
    raw: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    model: str
    count: int
