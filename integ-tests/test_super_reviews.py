import uuid

from _api_client import request_json


def test_reviews_super_returns_list():
    payload = request_json("/reviews-super")
    assert isinstance(payload, list)


def test_reviews_super_post_and_get_roundtrip():
    super_seller = request_json(
        "/super-sellers",
        method="POST",
        payload={"name": f"SuperSeller {uuid.uuid4().hex[:8]}"},
        expected_status=201,
    )

    offer = request_json(
        "/offers",
        method="POST",
        payload={
            "title": f"Super Offer {uuid.uuid4().hex[:8]}",
            "description": "Offer for super review test",
            "price": 99.99,
        },
        expected_status=201,
    )

    request_json(
        "/offers-super",
        method="PATCH",
        payload={"offerId": offer["id"], "superSellerId": super_seller["id"]},
        expected_status=200,
    )

    product = request_json(
        "/products",
        method="POST",
        payload={
            "name": f"Super Review Product {uuid.uuid4().hex[:8]}",
            "description": "Created for super review test",
            "price": 49.99,
        },
        expected_status=201,
    )

    created = request_json(
        "/reviews-super",
        method="POST",
        payload={
            "productId": product["id"],
            "rating": 5,
            "comment": "Super review comment",
            "authorName": "Super Tester",
            "offerId": offer["id"],
        },
        expected_status=201,
    )

    assert isinstance(created, dict)
    assert isinstance(created.get("id"), int)
    assert created["rating"] == 5
    assert created["comment"] == "Super review comment"
    assert created["authorName"] == "Super Tester"
    assert created["offerId"] == offer["id"]
    assert isinstance(created["createdAt"], str)

    reviews = request_json("/reviews-super", method="GET", expected_status=200)
    assert isinstance(reviews, list)

    matching = [r for r in reviews if r.get("id") == created["id"]]
    assert len(matching) == 1


def test_reviews_super_post_fails_without_super_seller_offer():
    offer = request_json(
        "/offers",
        method="POST",
        payload={
            "title": f"Normal Offer {uuid.uuid4().hex[:8]}",
            "description": "Offer without super seller",
            "price": 19.99,
        },
        expected_status=201,
    )

    product = request_json(
        "/products",
        method="POST",
        payload={
            "name": f"Product {uuid.uuid4().hex[:8]}",
            "description": "Created for error test",
            "price": 9.99,
        },
        expected_status=201,
    )

    request_json(
        "/reviews-super",
        method="POST",
        payload={
            "productId": product["id"],
            "rating": 3,
            "offerId": offer["id"],
        },
        expected_status=400,
    )


def test_reviews_super_post_fails_with_nonexistent_offer():
    product = request_json(
        "/products",
        method="POST",
        payload={
            "name": f"Product {uuid.uuid4().hex[:8]}",
            "description": "Created for error test",
            "price": 9.99,
        },
        expected_status=201,
    )

    request_json(
        "/reviews-super",
        method="POST",
        payload={
            "productId": product["id"],
            "rating": 3,
            "offerId": 999999,
        },
        expected_status=404,
    )


def test_reviews_super_post_fails_with_nonexistent_product():
    request_json(
        "/reviews-super",
        method="POST",
        payload={
            "productId": 999999,
            "rating": 3,
            "offerId": 1,
        },
        expected_status=404,
    )
