#!/bin/bash
# MasteryGraph PostgreSQL Backup Script
# Run daily via cron to create timestamped pg_dump files

set -euo pipefail

DB_NAME="masterygraph"
DB_USER="masterygraph"
BACKUP_DIR="/root/.openclaw/workspace/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/masterygraph_$DATE.sql.gz"
RETENTION_DAYS=30

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Run pg_dump and compress
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" --no-owner --no-privileges | gzip > "$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    echo "[$(date)] Backup successful: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
else
    echo "[$(date)] Backup FAILED: $BACKUP_FILE"
    exit 1
fi

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "masterygraph_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Log backup count
COUNT=$(find "$BACKUP_DIR" -name "masterygraph_*.sql.gz" | wc -l)
echo "[$(date)] Total backups: $COUNT (retention: $RETENTION_DAYS days)"
