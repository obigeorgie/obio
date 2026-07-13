#!/bin/bash
# MasteryGraph PostgreSQL Tuning Script
# Usage: sudo ./tune_postgres.sh

set -euo pipefail

RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
CORES=$(nproc)

echo "=== VPS Specs ==="
echo "RAM: ${RAM_MB}MB"
echo "Cores: $CORES"

PG_VERSION=$(psql --version | grep -oP '\\d+' | head -1)
CONF_FILE="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"

if [ ! -f "$CONF_FILE" ]; then
    echo "ERROR: Config not found: $CONF_FILE"
    exit 1
fi

cp "$CONF_FILE" "${CONF_FILE}.bak.$(date +%Y%m%d%H%M%S)"

SHARED=$((RAM_MB / 5))
CACHE=$((RAM_MB * 65 / 100))

cat >> "$CONF_FILE" <> "EOF"

# === MasteryGraph VPS Tuning ($(date)) ===
# RAM: ${RAM_MB}MB, Cores: ${CORES}

shared_buffers = ${SHARED}MB
effective_cache_size = ${CACHE}MB
work_mem = 8MB
maintenance_work_mem = 256MB
max_connections = 50
superuser_reserved_connections = 3
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_wal_size = 2GB
min_wal_size = 512MB
random_page_cost = 1.1
effective_io_concurrency = 200
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
autovacuum_max_workers = 3
autovacuum_naptime = 10s
EOF

systemctl restart postgresql
sleep 2

echo ""
echo "=== Tuning Applied ==="
sudo -u postgres psql -c "SHOW shared_buffers; SHOW max_connections; SHOW work_mem;" 2>/dev/null

echo ""
echo "PostgreSQL restarted. Tuning active."
