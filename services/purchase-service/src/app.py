import json
import logging
import os
from typing import Any

from flask import Flask, jsonify, request
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


def _init_db() -> None:
    conn = _get_db_connection()
    if conn is None:
        _json_log("database init skipped", reason="no connection")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS purchase (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    offer_id INT NOT NULL,
                    quantity INT NOT NULL,
                    price_per_unit DOUBLE PRECISION NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    super_seller_id INT NULL
                )
                """
            )
        conn.commit()
        _json_log("database init complete", table="purchase")
    except Exception as e:
        _json_log("database init failed", error=str(e))
    finally:
        conn.close()


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


def _fetch_purchases_filtered_from_db(offer_id: int | None = None, user_id: int | None = None, super_seller_id: int | None = None) -> list[dict[str, Any]] | None:
    conn = _get_db_connection()
    if conn is None:
        return None

    try:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            where_clauses = []
            params = []
            if offer_id is not None:
                where_clauses.append('offer_id = %s')
                params.append(offer_id)
            if user_id is not None:
                where_clauses.append('user_id = %s')
                params.append(user_id)
            if super_seller_id is not None:
                where_clauses.append('super_seller_id = %s')
                params.append(super_seller_id)

            base = 'SELECT id, user_id as userId, offer_id as offerId, quantity, price_per_unit as pricePerUnit, status FROM purchase'
            if where_clauses:
                base = f"{base} WHERE {' AND '.join(where_clauses)}"
            base = f"{base} ORDER BY id"

            cur.execute(base, tuple(params))
            rows = cur.fetchall()

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


def _create_purchase_in_db(user_id: int, offer_id: int, quantity: int, price_per_unit: float, status: str, super_seller_id: int | None = None) -> dict[str, Any] | None:
    conn = _get_db_connection()
    if conn is None:
        return None

    try:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(
                "INSERT INTO purchase (user_id, offer_id, quantity, price_per_unit, status, super_seller_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, user_id as userId, offer_id as offerId, quantity, price_per_unit as pricePerUnit, status, super_seller_id",
                (user_id, offer_id, quantity, price_per_unit, status, super_seller_id),
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
                "superSellerId": row.get("super_seller_id"),
            }
    except Exception as e:
        _json_log("database insert failed", error=str(e))
        return None
    finally:
        conn.close()


def _fetch_purchases_super_from_db() -> list[dict[str, Any]] | None:
    conn = _get_db_connection()
    if conn is None:
        return None

    try:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT id, user_id as userId, offer_id as offerId, quantity, price_per_unit as pricePerUnit, status, super_seller_id FROM purchase WHERE super_seller_id IS NOT NULL ORDER BY id")
            rows = cur.fetchall()

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
                    "superSellerId": row.get("super_seller_id"),
                })

            return results
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
    # Support optional filtering via query params: offerId, userId, superSellerId
    offer_id = request.args.get('offerId')
    user_id = request.args.get('userId')
    super_seller_id = request.args.get('superSellerId')

    def _parse_int(val: str | None) -> int | None:
        if val is None:
            return None
        try:
            return int(val)
        except Exception:
            return None

    offer_id_i = _parse_int(offer_id)
    user_id_i = _parse_int(user_id)
    super_seller_id_i = _parse_int(super_seller_id)

    purchases = None
    if offer_id_i is not None or user_id_i is not None or super_seller_id_i is not None:
        purchases = _fetch_purchases_filtered_from_db(offer_id=offer_id_i, user_id=user_id_i, super_seller_id=super_seller_id_i)
    else:
        purchases = _fetch_purchases_from_db()

    if purchases is None:
        # Fallback to hardcoded data and apply filters if any
        filtered = PURCHASES
        if offer_id_i is not None:
            filtered = [p for p in filtered if p.get('offerId') == offer_id_i]
        if user_id_i is not None:
            filtered = [p for p in filtered if p.get('userId') == user_id_i]
        if super_seller_id_i is not None:
            # fallback data doesn't include superSellerId, so return empty
            filtered = []

        _json_log("purchases fetched (hardcoded fallback)", endpoint="/purchases", count=len(filtered), source="fallback")
        return jsonify(filtered), 200

    _json_log("purchases fetched", endpoint="/purchases", count=len(purchases), source="database")
    return jsonify(purchases), 200


@app.post("/purchases")
def create_purchase() -> Any:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    user_id = payload.get("userId")
    offer_id = payload.get("offerId")
    quantity = payload.get("quantity")
    price_per_unit = payload.get("pricePerUnit")
    status = payload.get("status", "completed")
    super_seller_id = payload.get("superSellerId")

    if not (isinstance(user_id, int) and isinstance(offer_id, int) and isinstance(quantity, int) and (isinstance(price_per_unit, (int, float)) or isinstance(price_per_unit, str)) and isinstance(status, str)):
        return jsonify({"error": "Fields userId, offerId, quantity, pricePerUnit, status are required and should be correct types"}), 400

    if super_seller_id is not None and not isinstance(super_seller_id, int):
        return jsonify({"error": "superSellerId must be an integer if provided"}), 400

    try:
        price_per_unit_f = float(price_per_unit)
    except Exception:
        return jsonify({"error": "pricePerUnit must be a number"}), 400

    created = _create_purchase_in_db(
        user_id=user_id,
        offer_id=offer_id,
        quantity=quantity,
        price_per_unit=price_per_unit_f,
        status=status,
        super_seller_id=super_seller_id,
    )
    if created is None:
        # If DB not available, return 503
        return jsonify({"error": "Could not create purchase"}), 503

    _json_log("purchase created", endpoint="/purchases", purchaseId=created.get('id'), source="database")
    return jsonify(created), 201


@app.get('/purchases/super')
def get_super_purchases() -> Any:
    purchases = _fetch_purchases_super_from_db()
    if purchases is None:
        _json_log("super purchases fetched (hardcoded fallback)", endpoint='/purchases/super', count=0, source='fallback')
        return jsonify([]), 200

    _json_log("super purchases fetched", endpoint='/purchases/super', count=len(purchases), source='database')
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
    _init_db()
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
