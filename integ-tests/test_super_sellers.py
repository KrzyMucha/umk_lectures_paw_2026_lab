import uuid

from _api_client import request_json


def test_super_sellers_get_returns_list():
    payload = request_json("/super-sellers")
    assert isinstance(payload, list)


def test_super_sellers_post_and_get_roundtrip():
    name = f"Seller {uuid.uuid4().hex[:8]}"
    created = request_json(
        "/super-sellers",
        method="POST",
        payload={"name": name},
        expected_status=201,
    )

    assert isinstance(created, dict)
    assert isinstance(created.get("id"), int)
    assert created["name"] == name
    assert created["isActive"] is True
    assert "createdAt" in created

    sellers = request_json("/super-sellers")
    matching = [s for s in sellers if s.get("id") == created["id"]]
    assert len(matching) == 1
