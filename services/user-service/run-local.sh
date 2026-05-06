#!/bin/bash
set -e

usage() {
    echo "Usage: $0 {start|stop|logs|logs-neo4j}"
    exit 1
}

case "${1:-start}" in
  start)
    echo "Starting user-service with Neo4J..."
    docker compose up -d
    
    echo "⏳ Waiting for Neo4J and user-service to be ready..."
    sleep 10
    
    echo "✅ Services started!"
    echo "  📡 API: http://localhost:8081"
    echo "  🗄️  Neo4J Browser: http://localhost:7474"
    echo "  🔌 Neo4J Bolt: neo4j://localhost:7687 (user: neo4j, pass: testpassword)"
    ;;
    
  stop)
    echo "Stopping user-service and Neo4J..."
    docker compose down
    echo "✅ Stopped."
    ;;
    
  logs)
    docker compose logs -f app
    ;;
    
  logs-neo4j)
    docker compose logs -f neo4j
    ;;
    
  *)
    usage
    ;;
esac
