import uuid

from _api_client import request_json


def test_product_reviews_returns_expected_shape():
    payload = request_json("/product-reviews")

    assert isinstance(payload, list)

    if len(payload) >= 1:
        first = payload[0]
        assert isinstance(first, dict)
        assert "id" in first
        assert "rating" in first
        assert "createdAt" in first
        assert isinstance(first["id"], int)
        assert isinstance(first["rating"], int)
        assert isinstance(first["createdAt"], str)


def test_product_reviews_get_and_post_roundtrip():
    product = request_json(
        "/products",
        method="POST",
        payload={
            "name": f"Review Test Product {uuid.uuid4().hex[:8]}",
            "description": "Created for review integration test",
            "price": 49.99,
        },
        expected_status=201,
    )

    product_id = product["id"]

    created = request_json(
        "/product-reviews",
        method="POST",
        payload={
            "productId": product_id,
            "rating": 4,
            "comment": "Integration test comment",
            "authorName": "Integration Tester",
        },
        expected_status=201,
    )

    assert isinstance(created, dict)
    assert isinstance(created.get("id"), int)
    assert created["rating"] == 4
    assert created["comment"] == "Integration test comment"
    assert created["authorName"] == "Integration Tester"
    assert isinstance(created["createdAt"], str)

    reviews = request_json("/product-reviews", method="GET", expected_status=200)
    assert isinstance(reviews, list)

    matching = [r for r in reviews if r.get("id") == created["id"]]
    assert len(matching) == 1
