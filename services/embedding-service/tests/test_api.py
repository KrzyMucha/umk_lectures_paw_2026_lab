import random
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def _random_vector(dim: int) -> list[float]:
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]


def _mock_query_result(points):
    result = MagicMock()
    result.points = points
    return result


def _make_point(id: int, raw: str, score: float):
    point = MagicMock()
    point.id = id
    point.payload = {"raw": raw}
    point.score = score
    return point


FAKE_OLLAMA_VECTOR = _random_vector(768)
FAKE_GEMINI_VECTOR = _random_vector(3072)

FAKE_MODELS = {
    "ollama": {"vector": "nomic-embed-text", "dim": 768, "embed": lambda t: FAKE_OLLAMA_VECTOR},
    "gemini": {"vector": "gemini-embedding-2", "dim": 3072, "embed": lambda t: FAKE_GEMINI_VECTOR},
}


@pytest.fixture()
def client():
    with patch("app.main.get_client") as mock_get_client, \
         patch("app.main.verify_collection"), \
         patch("app.main.MODELS", FAKE_MODELS):
        mock_qdrant = MagicMock()
        mock_get_client.return_value = mock_qdrant

        from app.main import app
        with TestClient(app) as c:
            yield c, mock_qdrant


class TestHealth:
    def test_returns_ok(self, client):
        c, _ = client
        resp = c.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestSearch:
    def test_ollama_returns_results(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([
            _make_point(1, "Wireless Mouse", 0.95),
            _make_point(2, "Mechanical Keyboard", 0.85),
        ])

        resp = c.get("/search", params={
            "query": "mouse",
            "model": "ollama",
            "limit": 2,
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["model"] == "ollama"
        assert body["count"] == 2
        assert body["results"][0]["id"] == 1
        assert body["results"][0]["raw"] == "Wireless Mouse"
        assert body["results"][0]["score"] == 0.95

    def test_gemini_returns_results(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([
            _make_point(3, "USB-C Hub", 0.9),
        ])

        resp = c.get("/search", params={
            "query": "hub",
            "model": "gemini",
            "limit": 1,
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["model"] == "gemini"
        assert body["count"] == 1

    def test_calls_qdrant_with_correct_params(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        c.get("/search", params={"query": "test", "model": "ollama", "limit": 7})

        mock_qdrant.query_points.assert_called_once_with(
            collection_name="ai-arxiv",
            query=FAKE_OLLAMA_VECTOR,
            using="nomic-embed-text",
            limit=7,
            with_payload=True,
        )

    def test_gemini_uses_named_vector(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        c.get("/search", params={"query": "test", "model": "gemini"})

        call_kwargs = mock_qdrant.query_points.call_args.kwargs
        assert call_kwargs["using"] == "gemini-embedding-2"
        assert "query_filter" not in call_kwargs

    def test_empty_results(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        resp = c.get("/search", params={"query": "nothing", "model": "ollama"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["results"] == []
        assert body["count"] == 0

    def test_default_limit_is_5(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        c.get("/search", params={"query": "test", "model": "ollama"})

        _, kwargs = mock_qdrant.query_points.call_args
        assert kwargs["limit"] == 5

    def test_invalid_model(self, client):
        c, _ = client
        resp = c.get("/search", params={"query": "test", "model": "invalid"})
        assert resp.status_code == 422

    def test_missing_query(self, client):
        c, _ = client
        resp = c.get("/search", params={"model": "ollama"})
        assert resp.status_code == 422

    def test_missing_model(self, client):
        c, _ = client
        resp = c.get("/search", params={"query": "test"})
        assert resp.status_code == 422

    def test_empty_query(self, client):
        c, _ = client
        resp = c.get("/search", params={"query": "", "model": "ollama"})
        assert resp.status_code == 422

    def test_limit_too_high(self, client):
        c, _ = client
        resp = c.get("/search", params={"query": "test", "model": "ollama", "limit": 200})
        assert resp.status_code == 422

    def test_limit_zero(self, client):
        c, _ = client
        resp = c.get("/search", params={"query": "test", "model": "ollama", "limit": 0})
        assert resp.status_code == 422
