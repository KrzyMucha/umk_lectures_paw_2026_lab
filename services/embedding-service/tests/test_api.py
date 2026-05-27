import random
from unittest.mock import ANY, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def _random_vector(dim: int) -> list[float]:
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]


def _mock_query_result(points):
    result = MagicMock()
    result.points = points
    return result


def _make_point(id: int, raw: str, score: float, model: str = "ollama"):
    point = MagicMock()
    point.id = id
    point.payload = {"raw": raw, "model": model}
    point.score = score
    return point


@pytest.fixture()
def client():
    with patch("app.main.get_client") as mock_get_client, \
         patch("app.main.ensure_collection"):
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

        resp = c.post("/search", json={
            "vector": _random_vector(768),
            "model": "ollama",
            "limit": 2,
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["model"] == "ollama"
        assert body["count"] == 2
        assert len(body["results"]) == 2
        assert body["results"][0]["id"] == 1
        assert body["results"][0]["raw"] == "Wireless Mouse"
        assert body["results"][0]["score"] == 0.95

    def test_gemini_returns_results(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([
            _make_point(3, "USB-C Hub", 0.9, model="gemini"),
        ])

        resp = c.post("/search", json={
            "vector": _random_vector(768),
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
        vec = _random_vector(768)

        c.post("/search", json={"vector": vec, "model": "ollama", "limit": 7})

        mock_qdrant.query_points.assert_called_once_with(
            collection_name="embeddings",
            query=vec,
            using="ollama",
            query_filter=ANY,
            limit=7,
            with_payload=True,
        )

    def test_filter_uses_model(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        c.post("/search", json={
            "vector": _random_vector(768),
            "model": "ollama",
        })

        call_kwargs = mock_qdrant.query_points.call_args.kwargs
        qf = call_kwargs["query_filter"]
        assert len(qf.must) == 1
        assert qf.must[0].key == "model"
        assert qf.must[0].match.value == "ollama"

    def test_empty_results(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        resp = c.post("/search", json={
            "vector": _random_vector(768),
            "model": "ollama",
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["results"] == []
        assert body["count"] == 0

    def test_default_limit_is_5(self, client):
        c, mock_qdrant = client
        mock_qdrant.query_points.return_value = _mock_query_result([])

        c.post("/search", json={
            "vector": _random_vector(768),
            "model": "ollama",
        })

        _, kwargs = mock_qdrant.query_points.call_args
        assert kwargs["limit"] == 5

    def test_wrong_dimension_ollama(self, client):
        c, _ = client
        resp = c.post("/search", json={
            "vector": [0.1, 0.2, 0.3],
            "model": "ollama",
        })
        assert resp.status_code == 400
        assert "expected 768" in resp.json()["detail"]
        assert "got 3" in resp.json()["detail"]

    def test_wrong_dimension_gemini(self, client):
        c, _ = client
        resp = c.post("/search", json={
            "vector": [0.1, 0.2, 0.3],
            "model": "gemini",
        })
        assert resp.status_code == 400
        assert "expected 768" in resp.json()["detail"]
        assert "got 3" in resp.json()["detail"]

    def test_invalid_model(self, client):
        c, _ = client
        resp = c.post("/search", json={
            "vector": [0.1],
            "model": "invalid",
        })
        assert resp.status_code == 422

    def test_missing_vector(self, client):
        c, _ = client
        resp = c.post("/search", json={"model": "ollama"})
        assert resp.status_code == 422

    def test_missing_model(self, client):
        c, _ = client
        resp = c.post("/search", json={"vector": [0.1]})
        assert resp.status_code == 422

    def test_limit_too_high(self, client):
        c, _ = client
        resp = c.post("/search", json={
            "vector": [0.1],
            "model": "ollama",
            "limit": 200,
        })
        assert resp.status_code == 422

    def test_limit_zero(self, client):
        c, _ = client
        resp = c.post("/search", json={
            "vector": [0.1],
            "model": "ollama",
            "limit": 0,
        })
        assert resp.status_code == 422
