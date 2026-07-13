#!/bin/bash
# Start the OBIO backend
# Environment variables are loaded from /root/.openclaw/.env (gitignored)
# Ensure that file exists and contains required secrets before running.

ENV_FILE="/root/.openclaw/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found. Create it with required secrets." >&2
    exit 1
fi

# Load environment
set -a
source "$ENV_FILE"
set +a

cd /root/.openclaw/workspace

# Validate required env vars
MISSING=0
for VAR in RESEND_API_KEY RESEND_FROM_EMAIL STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET; do
    if [ -z "${!VAR}" ]; then
        echo "ERROR: $VAR is not set in $ENV_FILE" >&2
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "Fix $ENV_FILE and try again." >&2
    exit 1
fi

# Auto-build DATABASE_URL if not set but components are
if [ -z "$DATABASE_URL" ] && [ -n "$POSTGRES_PASSWORD" ]; then
    export DATABASE_URL="postgresql://${POSTGRES_USER:-masterygraph}:${POSTGRES_PASSWORD}@${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-masterygraph}"
    echo "[DB] PostgreSQL: $DATABASE_URL" >&2
fi

exec /usr/bin/python3 -m uvicorn masterygraph_api:app --host 0.0.0.0 --port 8000
