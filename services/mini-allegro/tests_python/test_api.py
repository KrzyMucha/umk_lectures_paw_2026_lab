import json
import os
import urllib.error
import urllib.request


BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")


def _get_json(path: str):
    url = f"{BASE_URL}{path}"
    request = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise AssertionError(f"Request to {url} failed: {error}") from error

    assert status == 200, f"Expected HTTP 200 for {url}, got {status}"

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        raise AssertionError(f"Response from {url} is not valid JSON") from error

    return payload


def test_offers_returns_expected_shape():
    payload = _get_json("/offers")

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


def test_users_returns_expected_shape():
    payload = _get_json("/users")

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
