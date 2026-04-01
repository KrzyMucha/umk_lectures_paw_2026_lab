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
