import json
import logging
import os
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from flask import Flask, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor


app = Flask(__name__)


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("purchase-service")


PURCHASES_QUERY = """
    SELECT
        id,
        user_id AS "userId",
        offer_id AS "offerId",
        quantity,
        price_per_unit AS "pricePerUnit",
        quantity * price_per_unit AS "totalPrice",
        status
    FROM purchase
    ORDER BY id
"""

PURCHASE_BY_ID_QUERY = """
    SELECT
        id,
        user_id AS "userId",
        offer_id AS "offerId",
        quantity,
        price_per_unit AS "pricePerUnit",
        quantity * price_per_unit AS "totalPrice",
        status
    FROM purchase
    WHERE id = %s
"""


def _json_log(message: str, **fields: Any) -> None:
    payload = {"message": message, **fields}
    logger.info(json.dumps(payload, ensure_ascii=True))


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    parsed_url = urlparse(database_url)
    query_params = [
        (key, value)
        for key, value in parse_qsl(parsed_url.query, keep_blank_values=True)
        if key not in {"serverVersion", "charset"}
    ]
    normalized_query = urlencode(query_params)
    return urlunparse(parsed_url._replace(query=normalized_query))


def _fetch_all_purchases() -> list[dict[str, Any]]:
    with psycopg2.connect(_get_database_url(), cursor_factory=RealDictCursor) as connection:
        with connection.cursor() as cursor:
            cursor.execute(PURCHASES_QUERY)
            return [dict(row) for row in cursor.fetchall()]


def _fetch_purchase_by_id(purchase_id: int) -> dict[str, Any] | None:
    with psycopg2.connect(_get_database_url(), cursor_factory=RealDictCursor) as connection:
        with connection.cursor() as cursor:
            cursor.execute(PURCHASE_BY_ID_QUERY, (purchase_id,))
            row = cursor.fetchone()
            return dict(row) if row is not None else None


@app.get("/health")
def health() -> Any:
    _json_log("health check", endpoint="/health", status="ok")
    return jsonify({"status": "ok"}), 200


@app.get("/purchases")
def get_purchases() -> Any:
    try:
        purchases = _fetch_all_purchases()
    except (psycopg2.Error, RuntimeError) as exc:
        _json_log("purchases query failed", endpoint="/purchases", error=str(exc))
        return jsonify({"error": "purchase database unavailable"}), 503

    _json_log("purchases fetched", endpoint="/purchases", count=len(purchases))
    return jsonify(purchases), 200


@app.get("/purchases/<int:purchase_id>")
def get_purchase_by_id(purchase_id: int) -> Any:
    try:
        purchase = _fetch_purchase_by_id(purchase_id)
    except (psycopg2.Error, RuntimeError) as exc:
        _json_log("purchase query failed", endpoint="/purchases/{id}", purchaseId=purchase_id, error=str(exc))
        return jsonify({"error": "purchase database unavailable"}), 503

    if purchase is None:
        return jsonify({"error": "Purchase not found"}), 404

    _json_log("purchase fetched", endpoint="/purchases/{id}", purchaseId=purchase_id)
    return jsonify(purchase), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
