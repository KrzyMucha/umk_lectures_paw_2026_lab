from _api_client import request_json


def test_offers_returns_expected_shape():
    payload = request_json("/offers")

    assert isinstance(payload, list)
    assert len(payload) >= 1

    first = payload[0]
    assert isinstance(first, dict)
    assert "title" in first
    assert "description" in first
    assert "price" in first
    assert isinstance(first["title"], str)
    assert isinstance(first["description"], str)
    assert isinstance(first["price"], (int, float))
