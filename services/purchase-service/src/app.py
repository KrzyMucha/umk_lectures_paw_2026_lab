import json
import logging
import os
from typing import Any

from flask import Flask, jsonify


app = Flask(__name__)


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("purchase-service")


PURCHASES: list[dict[str, Any]] = [
    {
        "id": 1,
        "userId": 101,
        "offerId": 201,
        "quantity": 2,
        "pricePerUnit": 19.99,
        "totalPrice": 39.98,
        "status": "completed",
    },
    {
        "id": 2,
        "userId": 102,
        "offerId": 202,
        "quantity": 1,
        "pricePerUnit": 149.0,
        "totalPrice": 149.0,
        "status": "pending",
    },
    {
        "id": 3,
        "userId": 103,
        "offerId": 201,
        "quantity": 4,
        "pricePerUnit": 7.5,
        "totalPrice": 30.0,
        "status": "completed",
    },
    {
        "id": 4,
        "userId": 104,
        "offerId": 203,
        "quantity": 1,
        "pricePerUnit": 599.99,
        "totalPrice": 599.99,
        "status": "cancelled",
    },
]


def _json_log(message: str, **fields: Any) -> None:
    payload = {"message": message, **fields}
    logger.info(json.dumps(payload, ensure_ascii=True))


def _find_purchase(purchase_id: int) -> dict[str, Any] | None:
    for purchase in PURCHASES:
        if purchase["id"] == purchase_id:
            return purchase
    return None


@app.get("/health")
def health() -> Any:
    _json_log("health check", endpoint="/health", status="ok")
    return jsonify({"status": "ok"}), 200


@app.get("/purchases")
def get_purchases() -> Any:
    _json_log("purchases fetched", endpoint="/purchases", count=len(PURCHASES))
    return jsonify(PURCHASES), 200


@app.get("/purchases/<int:purchase_id>")
def get_purchase_by_id(purchase_id: int) -> Any:
    purchase = _find_purchase(purchase_id)
    if purchase is None:
        return jsonify({"error": "Purchase not found"}), 404

    _json_log("purchase fetched", endpoint="/purchases/{id}", purchaseId=purchase_id)
    return jsonify(purchase), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
