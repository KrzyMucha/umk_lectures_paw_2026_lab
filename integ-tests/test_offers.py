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
        assert "superSellerId" in first
        assert isinstance(first["title"], str)
        assert isinstance(first["description"], (str, type(None)))
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


def test_offers_super_returns_empty_list():
    payload = request_json("/offers-super")
    assert isinstance(payload, list)


def test_offers_super_patch_assigns_super_seller():
    # Create a SuperSeller
    seller = request_json(
        "/super-sellers",
        method="POST",
        payload={"name": f"TestSeller {uuid.uuid4().hex[:8]}"},
        expected_status=201,
    )
    assert isinstance(seller.get("id"), int)

    # Create an Offer
    offer = request_json(
        "/offers",
        method="POST",
        payload={
            "title": f"Super Offer {uuid.uuid4().hex[:8]}",
            "description": "For super seller test",
            "price": 99.99,
        },
        expected_status=201,
    )
    assert offer.get("superSellerId") is None

    # PATCH to assign SuperSeller
    patched = request_json(
        "/offers-super",
        method="PATCH",
        payload={"offerId": offer["id"], "superSellerId": seller["id"]},
        expected_status=200,
    )
    assert patched["id"] == offer["id"]
    assert patched["superSellerId"] == seller["id"]

    # Verify it appears in GET /offers-super
    super_offers = request_json("/offers-super")
    matching = [o for o in super_offers if o.get("id") == offer["id"]]
    assert len(matching) == 1
    assert matching[0]["superSellerId"] == seller["id"]
