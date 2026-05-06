#!/bin/bash
# Neo4J startup script for Compute Engine VM (PRODUCTION)
# Initializes Docker, downloads and starts Neo4J container

set -e

# Update system and install required packages
apt-get update
apt-get install -y docker.io curl

# Start Docker and enable on boot
systemctl start docker
systemctl enable docker

# Format and mount data disk
mkfs.ext4 -F /dev/sdb
mkdir -p /mnt/neo4j-data
mount /dev/sdb /mnt/neo4j-data

# Create directory structure for Neo4J
mkdir -p /mnt/neo4j-data/{data,logs,import,conf}
chmod -R 755 /mnt/neo4j-data

# Create Neo4J configuration optimized for production
cat > /mnt/neo4j-data/conf/neo4j.conf << 'EOF'
# Network configuration
server.default_listen_address=0.0.0.0
server.default_advertised_address=HOSTNAME_PLACEHOLDER
dbms.default_database=neo4j

# Memory settings optimized for e2-standard-2 (7.5GB RAM)
dbms.memory.heap.initial_size=2048m
dbms.memory.heap.max_size=2048m

# Performance tuning
dbms.memory.pagecache.size=2g
dbms.transaction.bookmark_ready_timeout=300s
dbms.database.tx_log.rotation.flush_buffer_size=262144
EOF

# Start Neo4J container with persistent volumes and restart policy
docker run -d \
  --name neo4j \
  --restart always \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/${neo4j_password} \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_server_memory_heap_initial__size=2G \
  -e NEO4J_server_memory_heap_max__size=2G \
  -e NEO4J_server_memory_pagecache_size=2G \
  -v /mnt/neo4j-data/data:/var/lib/neo4j/data \
  -v /mnt/neo4j-data/logs:/var/lib/neo4j/logs \
  -v /mnt/neo4j-data/import:/var/lib/neo4j/import \
  -v /mnt/neo4j-data/conf:/var/lib/neo4j/conf \
  neo4j:5.15-enterprise

# Wait for Neo4J to start
sleep 30

# Verify Neo4J is running
docker exec neo4j cypher-shell -a bolt://localhost:${neo4j_port} -u neo4j -p ${neo4j_password} "MATCH (n) RETURN COUNT(n) AS count;"

# Enable automatic backups
mkdir -p /mnt/neo4j-data/backups
cat > /etc/cron.daily/neo4j-backup << 'EOF_CRON'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec neo4j neo4j-admin database backup --from-path=/var/lib/neo4j/backups neo4j > /mnt/neo4j-data/backups/backup_${TIMESTAMP}.log 2>&1
EOF_CRON
chmod +x /etc/cron.daily/neo4j-backup

echo "Neo4J PROD instance started successfully"
echo "Bolt URI: neo4j://localhost:${neo4j_port}"
echo "Browser: http://localhost:7474/"
