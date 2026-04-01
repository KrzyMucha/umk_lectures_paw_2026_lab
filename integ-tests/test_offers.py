import uuid

from _api_client import request_json


def test_offers_returns_expected_shape():
    payload = request_json("/offers")

    assert isinstance(payload, list)

    if len(payload) >= 1:
        first = payload[0]
        assert isinstance(first, dict)
        assert "title" in first
        assert "description" in first
        assert "price" in first
        assert isinstance(first["title"], str)
        assert isinstance(first["description"], str)
        assert isinstance(first["price"], (int, float))


def test_offers_get_and_post_roundtrip():
    created = request_json(
        "/offers",
        method="POST",
        payload={
            "title": f"Integration Offer {uuid.uuid4().hex[:8]}",
            "description": "Created from integration test",
            "price": 199.99,
        },
        expected_status=201,
    )

    assert isinstance(created, dict)
    assert isinstance(created.get("id"), int)
    assert created["title"].startswith("Integration Offer")
    assert created["description"] == "Created from integration test"
    assert isinstance(created["price"], (int, float))

    offers = request_json("/offers", method="GET", expected_status=200)
    assert isinstance(offers, list)

    matching = [o for o in offers if o.get("id") == created["id"]]
    assert len(matching) == 1
