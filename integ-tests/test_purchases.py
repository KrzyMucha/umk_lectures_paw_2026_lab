import uuid

from _api_client import request_json


def test_purchases_returns_expected_shape():
    """
    Test that GET /purchases returns a list with correct schema.
    Monolith delegates to purchase-service, which queries from database.
    """
    payload = request_json("/purchases")

    assert isinstance(payload, list)
    assert len(payload) >= 1

    first = payload[0]
    assert isinstance(first, dict)
    assert "id" in first
    assert "userId" in first
    assert "offerId" in first
    assert "quantity" in first
    assert "pricePerUnit" in first
    assert "totalPrice" in first
    assert "status" in first

    # Verify types
    assert isinstance(first["id"], int)
    assert isinstance(first["userId"], int)
    assert isinstance(first["offerId"], int)
    assert isinstance(first["quantity"], int)
    assert isinstance(first["pricePerUnit"], (int, float))
    assert isinstance(first["totalPrice"], (int, float))
    assert isinstance(first["status"], str)


def test_purchases_get_by_id():
    """
    Test that GET /purchases/{id} returns a single purchase.
    Monolith delegates to purchase-service, which queries from database.
    """
    # First get the list to find a valid ID
    purchases = request_json("/purchases")
    assert len(purchases) >= 1

    first_id = purchases[0]["id"]

    # Now get by ID
    purchase = request_json(f"/purchases/{first_id}")

    assert isinstance(purchase, dict)
    assert purchase["id"] == first_id
    assert "userId" in purchase
    assert "offerId" in purchase
    assert "quantity" in purchase
    assert "pricePerUnit" in purchase
    assert "totalPrice" in purchase
    assert "status" in purchase


def test_purchases_nonexistent_id_returns_404():
    """Test that GET /purchases/{nonexistent} returns 404."""
    # Use a very high ID that shouldn't exist
    response = request_json(
        "/purchases/999999999",
        expected_status=404,
    )

    assert isinstance(response, dict)
    assert "error" in response


def test_purchases_consistency():
    """
    Test that multiple calls to /purchases return consistent data.
    This verifies that the purchase-service is reading from the same database
    and returning consistent results.
    """
    first_call = request_json("/purchases")
    second_call = request_json("/purchases")

    assert len(first_call) == len(second_call)

    # Check that the first few items are the same
    for i in range(min(3, len(first_call))):
        assert first_call[i]["id"] == second_call[i]["id"]
        assert first_call[i]["userId"] == second_call[i]["userId"]
        assert first_call[i]["offerId"] == second_call[i]["offerId"]
