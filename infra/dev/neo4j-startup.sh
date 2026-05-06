#!/bin/bash
# Neo4J startup script for Compute Engine VM
# Initializes Docker, downloads and starts Neo4J container

set -e

# Update system
apt-get update
apt-get install -y docker.io curl

# Start Docker
systemctl start docker
systemctl enable docker

# Format and mount data disk
mkfs.ext4 -F /dev/sdb
mkdir -p /mnt/neo4j-data
mount /dev/sdb /mnt/neo4j-data

# Create directory for Neo4J
mkdir -p /mnt/neo4j-data/{data,logs,import,conf}
chmod -R 755 /mnt/neo4j-data

# Create Neo4J configuration
cat > /mnt/neo4j-data/conf/neo4j.conf << 'EOF'
# Default network interface and protocols configuration
#*****************************************************************
# Network connector configuration
#*****************************************************************

# With default configuration Neo4j only accepts local connections.
# To accept non-local connections, uncomment this line:
server.default_listen_address=0.0.0.0
server.default_advertised_address=HOSTNAME_PLACEHOLDER
dbms.default_database=neo4j
#*****************************************************************
# Other settings
#*****************************************************************
dbms.memory.heap.initial_size=512m
dbms.memory.heap.max_size=512m
EOF

# Start Neo4J container with persistent volumes
docker run -d \
  --name neo4j \
  --restart unless-stopped \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/${neo4j_password} \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v /mnt/neo4j-data/data:/var/lib/neo4j/data \
  -v /mnt/neo4j-data/logs:/var/lib/neo4j/logs \
  -v /mnt/neo4j-data/import:/var/lib/neo4j/import \
  -v /mnt/neo4j-data/conf:/var/lib/neo4j/conf \
  neo4j:5.15-community

# Wait for Neo4J to start
sleep 30

# Verify Neo4J is running
docker exec neo4j cypher-shell -a bolt://localhost:${neo4j_port} -u neo4j -p ${neo4j_password} "MATCH (n) RETURN COUNT(n) AS count;"

echo "Neo4J started successfully"
echo "Bolt URI: neo4j://localhost:${neo4j_port}"
echo "Browser: http://localhost:7474/"
