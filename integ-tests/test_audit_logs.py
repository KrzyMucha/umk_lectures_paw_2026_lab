import json
import os
import urllib.error
import urllib.request

AUDIT_BASE_URL = os.getenv("AUDIT_LOG_SERVICE_URL", "http://localhost:8080").rstrip("/")


def _request(path: str, method: str = "GET", payload: dict | None = None, expected_status: int = 200):
    url = f"{AUDIT_BASE_URL}{path}"
    body = None
    headers = {}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, method=method, data=body, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            status = response.getcode()
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        raw_body = error.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise AssertionError(f"Request to {url} failed: {error}") from error

    assert status == expected_status, (
        f"Expected HTTP {expected_status} for {url}, got {status}, body={raw_body}"
    )

    return json.loads(raw_body)


# --- Health ---

def test_health():
    result = _request("/health")
    assert result["status"] == "ok"


# --- POST /logs ---

def test_create_log_product():
    result = _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "CREATE",
        "endpoint": "/products/1",
        "payload": {"id": 1, "name": "Laptop", "description": "Gaming laptop", "price": 3499.99},
    }, expected_status=201)

    assert "id" in result
    assert isinstance(result["id"], str)


def test_create_log_user():
    result = _request("/logs", method="POST", payload={
        "entity": "user",
        "operation": "CREATE",
        "endpoint": "/users/10",
        "payload": {"id": 10, "email": "jan@example.com", "firstName": "Jan", "lastName": "Kowalski", "isSuperSeller": False},
    }, expected_status=201)

    assert "id" in result


def test_create_log_update_delta():
    result = _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "UPDATE",
        "endpoint": "/products/1",
        "payload": {"price": 2999.99},
    }, expected_status=201)

    assert "id" in result


def test_create_log_delete_no_payload():
    result = _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "DELETE",
        "endpoint": "/products/1",
        "payload": None,
    }, expected_status=201)

    assert "id" in result


def test_create_log_purchase():
    result = _request("/logs", method="POST", payload={
        "entity": "purchase",
        "operation": "CREATE",
        "endpoint": "/purchases/5",
        "payload": {"id": 5, "userId": 10, "offerId": 20, "quantity": 2, "pricePerUnit": 19.99, "totalPrice": 39.98, "status": "pending"},
    }, expected_status=201)

    assert "id" in result


def test_create_log_review():
    result = _request("/logs", method="POST", payload={
        "entity": "review",
        "operation": "CREATE",
        "endpoint": "/product-reviews/3",
        "payload": {"id": 3, "productId": 1, "offerId": 20, "rating": 5, "comment": "Świetny!", "authorName": "Jan", "createdAt": "2026-05-13T10:00:00Z"},
    }, expected_status=201)

    assert "id" in result


# --- Walidacja ---

def test_invalid_entity_returns_400():
    _request("/logs", method="POST", payload={
        "entity": "unknown",
        "operation": "CREATE",
        "endpoint": "/unknown/1",
        "payload": {"id": 1},
    }, expected_status=400)


def test_invalid_operation_returns_400():
    _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "INVALID",
        "endpoint": "/products/1",
        "payload": {"id": 1},
    }, expected_status=400)


def test_delete_with_payload_returns_400():
    _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "DELETE",
        "endpoint": "/products/1",
        "payload": {"id": 1},
    }, expected_status=400)


def test_create_without_payload_returns_400():
    _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "CREATE",
        "endpoint": "/products/1",
        "payload": None,
    }, expected_status=400)


def test_missing_endpoint_returns_400():
    _request("/logs", method="POST", payload={
        "entity": "product",
        "operation": "CREATE",
        "payload": {"id": 1},
    }, expected_status=400)


# --- GET /logs ---

def test_get_logs_returns_list():
    result = _request("/logs")
    assert isinstance(result, list)


def test_get_logs_shape():
    result = _request("/logs")
    assert len(result) >= 1

    first = result[0]
    assert "id" in first
    assert "timestamp" in first
    assert "entity" in first
    assert "operation" in first
    assert "endpoint" in first


def test_get_logs_filter_by_entity():
    result = _request("/logs?entity=product")
    assert isinstance(result, list)
    for log in result:
        assert log["entity"] == "product"


def test_get_logs_filter_by_operation():
    result = _request("/logs?operation=CREATE")
    assert isinstance(result, list)
    for log in result:
        assert log["operation"] == "CREATE"


def test_get_logs_filter_by_entity_and_operation():
    result = _request("/logs?entity=product&operation=DELETE")
    assert isinstance(result, list)
    for log in result:
        assert log["entity"] == "product"
        assert log["operation"] == "DELETE"


def test_get_logs_invalid_entity_returns_400():
    _request("/logs?entity=unknown", expected_status=400)


def test_get_logs_delete_has_no_payload():
    result = _request("/logs?operation=DELETE")
    assert isinstance(result, list)
    for log in result:
        assert log.get("payload") is None
