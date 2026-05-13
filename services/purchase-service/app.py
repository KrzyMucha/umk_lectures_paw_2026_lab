from flask import Flask, jsonify, abort
import os

app = Flask(__name__)

PURCHASES = [
    {"id": 1, "status": "paid", "total": 199.99},
    {"id": 2, "status": "pending", "total": 49.90},
    {"id": 3, "status": "cancelled", "total": 9.99},
]


@app.get("/purchases")
def list_purchases():
    return jsonify(PURCHASES)


@app.get("/purchases/<int:purchase_id>")
def get_purchase(purchase_id: int):
    for purchase in PURCHASES:
        if purchase["id"] == purchase_id:
            return jsonify(purchase)
    abort(404)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
