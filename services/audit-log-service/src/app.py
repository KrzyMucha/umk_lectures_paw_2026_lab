import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from elasticsearch import Elasticsearch, ConnectionError, TransportError
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("audit-log-service")

VALID_ENTITIES = {"product", "purchase", "review", "user"}
VALID_OPERATIONS = {"CREATE", "UPDATE", "DELETE"}
INDEX = "audit_logs"

es = Elasticsearch(os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"))


def _json_log(message: str, **fields: Any) -> None:
    logger.info(json.dumps({"message": message, **fields}, ensure_ascii=True))


def _ensure_index() -> None:
    if es.indices.exists(index=INDEX):
        return
    es.indices.create(index=INDEX, body={
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "entity":    {"type": "keyword"},
                "operation": {"type": "keyword"},
                "endpoint":  {"type": "keyword"},
                "payload":   {"type": "object", "dynamic": True}
            }
        }
    })


def _es_unavailable() -> Any:
    _json_log("elasticsearch unavailable")
    return jsonify({"error": "Elasticsearch is unavailable. The VM may be stopped."}), 503


@app.get("/health")
def health() -> Any:
    _json_log("health check", endpoint="/health", status="ok")
    return jsonify({"status": "ok"}), 200


@app.post("/logs")
def create_log() -> Any:
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    entity = body.get("entity")
    operation = body.get("operation")
    endpoint = body.get("endpoint")
    payload = body.get("payload")

    if entity not in VALID_ENTITIES:
        return jsonify({"error": f"Invalid entity. Must be one of: {sorted(VALID_ENTITIES)}"}), 400
    if operation not in VALID_OPERATIONS:
        return jsonify({"error": f"Invalid operation. Must be one of: {sorted(VALID_OPERATIONS)}"}), 400
    if not endpoint:
        return jsonify({"error": "endpoint is required"}), 400
    if operation == "DELETE" and payload is not None:
        return jsonify({"error": "payload must be null for DELETE operations"}), 400
    if operation != "DELETE" and payload is None:
        return jsonify({"error": "payload is required for CREATE and UPDATE operations"}), 400

    try:
        _ensure_index()

        doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity":    entity,
            "operation": operation,
            "endpoint":  endpoint,
            "payload":   payload,
        }

        result = es.index(index=INDEX, body=doc)
    except (ConnectionError, TransportError):
        return _es_unavailable()

    _json_log("log created", entity=entity, operation=operation, endpoint=endpoint)
    return jsonify({"id": result["_id"]}), 201


@app.get("/logs")
def get_logs() -> Any:
    entity = request.args.get("entity")
    operation = request.args.get("operation")

    filters = []
    if entity:
        if entity not in VALID_ENTITIES:
            return jsonify({"error": f"Invalid entity. Must be one of: {sorted(VALID_ENTITIES)}"}), 400
        filters.append({"term": {"entity": entity}})
    if operation:
        if operation not in VALID_OPERATIONS:
            return jsonify({"error": f"Invalid operation. Must be one of: {sorted(VALID_OPERATIONS)}"}), 400
        filters.append({"term": {"operation": operation}})

    query = {"bool": {"filter": filters}} if filters else {"match_all": {}}

    try:
        _ensure_index()

        result = es.search(index=INDEX, body={
            "query": query,
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": 100
        })
    except (ConnectionError, TransportError):
        return _es_unavailable()

    logs = [{"id": hit["_id"], **hit["_source"]} for hit in result["hits"]["hits"]]
    _json_log("logs fetched", count=len(logs))
    return jsonify(logs), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
