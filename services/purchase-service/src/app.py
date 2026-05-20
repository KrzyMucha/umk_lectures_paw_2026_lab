import json
import logging
import os
from typing import Any

from flask import Flask, jsonify
import psycopg


app = Flask(__name__)


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("purchase-service")


# Hardcoded data as fallback
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


def _get_db_connection() -> psycopg.Connection | None:
    """
    Get a connection to the database using DATABASE_URL.
    Returns None if DATABASE_URL is not set or connection fails.
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        return None
    
    try:
        return psycopg.connect(database_url)
    except Exception as e:
        _json_log("database connection failed", error=str(e))
        return None


def _fetch_purchases_from_db() -> list[dict[str, Any]] | None:
    """
    Fetch all purchases from the database.
    Returns None if database connection fails.
    """
    conn = _get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT id, user_id as userId, offer_id as offerId, quantity, price_per_unit as pricePerUnit, status FROM purchase ORDER BY id")
            rows = cur.fetchall()
            
            # Compute totalPrice for each row
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "userId": row["userId"],
                    "offerId": row["offerId"],
                    "quantity": row["quantity"],
                    "pricePerUnit": float(row["pricePerUnit"]),
                    "totalPrice": float(row["quantity"] * row["pricePerUnit"]),
                    "status": row["status"],
                })
            
            return results
    except Exception as e:
        _json_log("database query failed", error=str(e))
        return None
    finally:
        conn.close()


def _fetch_purchase_by_id_from_db(purchase_id: int) -> dict[str, Any] | None:
    """
    Fetch a single purchase from the database by ID.
    Returns None if not found or connection fails.
    """
    conn = _get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(
                "SELECT id, user_id as userId, offer_id as offerId, quantity, price_per_unit as pricePerUnit, status FROM purchase WHERE id = %s",
                (purchase_id,)
            )
            row = cur.fetchone()
            
            if row is None:
                return None
            
            return {
                "id": row["id"],
                "userId": row["userId"],
                "offerId": row["offerId"],
                "quantity": row["quantity"],
                "pricePerUnit": float(row["pricePerUnit"]),
                "totalPrice": float(row["quantity"] * row["pricePerUnit"]),
                "status": row["status"],
            }
    except Exception as e:
        _json_log("database query failed", error=str(e))
        return None
    finally:
        conn.close()


def _find_purchase(purchase_id: int) -> dict[str, Any] | None:
    """Fallback to hardcoded data if database is not available."""
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
    purchases = _fetch_purchases_from_db()
    
    if purchases is None:
        # Fallback to hardcoded data
        _json_log("purchases fetched (hardcoded fallback)", endpoint="/purchases", count=len(PURCHASES), source="fallback")
        return jsonify(PURCHASES), 200
    
    _json_log("purchases fetched", endpoint="/purchases", count=len(purchases), source="database")
    return jsonify(purchases), 200


@app.get("/purchases/<int:purchase_id>")
def get_purchase_by_id(purchase_id: int) -> Any:
    purchase = _fetch_purchase_by_id_from_db(purchase_id)
    
    if purchase is None:
        # Try fallback to hardcoded data
        purchase = _find_purchase(purchase_id)
        if purchase is None:
            return jsonify({"error": "Purchase not found"}), 404
        
        _json_log("purchase fetched (hardcoded fallback)", endpoint="/purchases/{id}", purchaseId=purchase_id, source="fallback")
        return jsonify(purchase), 200
    
    _json_log("purchase fetched", endpoint="/purchases/{id}", purchaseId=purchase_id, source="database")
    return jsonify(purchase), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
