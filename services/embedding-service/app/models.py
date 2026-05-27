from pydantic import BaseModel


class SearchResultItem(BaseModel):
    id: int
    raw: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    model: str
    count: int
