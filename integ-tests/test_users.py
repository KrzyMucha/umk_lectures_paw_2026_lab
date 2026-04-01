import uuid

def test_users_post_creates_random_user():
    token = uuid.uuid4().hex[:10]
    email = f"integration.user.{token}@example.com"

    created = request_json(
        "/users",
        method="POST",
        payload={
            "email": email,
            "firstName": "Integration",
            "lastName": f"User{token[:4]}",
            "roles": ["ROLE_CUSTOMER"],
        },
        expected_status=201,
    )

    assert isinstance(created, dict)
    assert isinstance(created.get("id"), int)
    assert created["email"] == email
    assert created["firstName"] == "Integration"
    assert created["lastName"].startswith("User")
    assert isinstance(created["roles"], list)
    assert "ROLE_CUSTOMER" in created["roles"]

from _api_client import request_json


def test_users_returns_expected_shape():
    payload = request_json("/users")

    assert isinstance(payload, list)
    assert len(payload) >= 1

    first = payload[0]
    assert isinstance(first, dict)
    assert "email" in first
    assert "firstName" in first
    assert "lastName" in first
    assert "roles" in first
    assert isinstance(first["email"], str)
    assert isinstance(first["firstName"], str)
    assert isinstance(first["lastName"], str)
    assert isinstance(first["roles"], list)