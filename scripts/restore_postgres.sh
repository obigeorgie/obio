#!/bin/bash
# MasteryGraph PostgreSQL Restore Script
# Usage: ./restore_postgres.sh <backup_file>

set -euo pipefail

DB_NAME="masterygraph"
DB_USER="masterygraph"
BACKUP_DIR="/root/.openclaw/workspace/backups"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -1t "$BACKUP_DIR"/masterygraph_*.sql.gz 2>/dev/null | head -10 || echo "  (none)"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will DROP and recreate the $DB_NAME database."
echo "All existing data will be lost."
read -p "Are you sure? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "[$(date)] Starting restore from $BACKUP_FILE..."

# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restore from backup
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | psql -h localhost -U "$DB_USER" -d "$DB_NAME"
else
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"
fi

echo "[$(date)] Restore complete."

# Verify
COUNT=$(psql -h localhost -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM users;" | xargs)
echo "Users in restored database: $COUNT"
