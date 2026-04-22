import os
from typing import Any

from flask import Flask, jsonify


app = Flask(__name__)


OFFERS: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Uzywany laptop 16GB RAM",
        "description": "Sprawny, bateria po wymianie.",
        "price": 2499.99,
    },
    {
        "id": 2,
        "title": "Monitor 27 cali IPS",
        "description": "Rozdzielczosc 2560x1440, 75Hz.",
        "price": 899.0,
    },
    {
        "id": 3,
        "title": "Klawiatura mechaniczna",
        "description": "Switche linearne, podswietlenie RGB.",
        "price": 329.5,
    },
    {
        "id": 4,
        "title": "Mysz bezprzewodowa",
        "description": None,
        "price": 159.99,
    },
]


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"}), 200


@app.get("/offers")
def get_offers() -> Any:
    return jsonify(OFFERS), 200


@app.get("/offers/<int:offer_id>")
def get_offer_by_id(offer_id: int) -> Any:
    for offer in OFFERS:
        if offer["id"] == offer_id:
            return jsonify(offer), 200

    return jsonify({"error": "Offer not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)