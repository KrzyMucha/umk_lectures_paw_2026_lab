import uuid

from _api_client import request_json


def test_products_get_and_post_roundtrip():
    created = request_json(
        "/products",
        method="POST",
        payload={
            "name": f"Integration Product {uuid.uuid4().hex[:8]}",
            "description": "Created from integration test",
            "price": 123.45,
        },
        expected_status=201,
    )

    assert isinstance(created, dict)
    assert isinstance(created.get("id"), int)
    assert created["name"].startswith("Integration Product")
    assert created["description"] == "Created from integration test"
    assert isinstance(created["price"], (int, float))

    products = request_json("/products", method="GET", expected_status=200)
    assert isinstance(products, list)

    matching = [product for product in products if product.get("id") == created["id"]]
    assert len(matching) == 1
