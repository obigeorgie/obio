#!/bin/bash
# Start the OBIO backend
# REQUIRED: Set these environment variables before running:
#   export RESEND_API_KEY="..."
#   export RESEND_FROM_EMAIL="OBIO <admin@obiomacare.com>"
#   export OPENAI_API_KEY="..."  (optional, for OpenAI fallback)
#   export STRIPE_SECRET_KEY="..."
#   export STRIPE_WEBHOOK_SECRET="..."
#   export SENTRY_DSN="..."  (optional)
#   export OPENROUTER_API_KEY="..."  (for AI tutor)
#
# PostgreSQL (production database):
#   export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
#   OR:
#   export POSTGRES_HOST="localhost"
#   export POSTGRES_PORT="5432"
#   export POSTGRES_USER="masterygraph"
#   export POSTGRES_PASSWORD="..."
#   export POSTGRES_DB="masterygraph"
#
# If no PostgreSQL config, falls back to SQLite (masterygraph.db)
# Set them in ~/.bashrc, /etc/environment, or a .env file (gitignored)

cd /root/.openclaw/workspace

# Validate required env vars
MISSING=0
for VAR in RESEND_API_KEY RESEND_FROM_EMAIL STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET; do
    if [ -z "${!VAR}" ]; then
        echo "ERROR: $VAR is not set" >&2
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "Set required env vars and try again." >&2
    exit 1
fi

# AI Tutor: OpenRouter configuration
if [ -n "$OPENROUTER_API_KEY" ]; then
    export LLM_API_BASE="${LLM_API_BASE:-https://openrouter.ai/api/v1}"
    export LLM_API_KEY="${LLM_API_KEY:-$OPENROUTER_API_KEY}"
    export LLM_MODEL="${LLM_MODEL:-meta-llama/llama-3.1-8b-instruct}"
else
    export LLM_API_BASE="${LLM_API_BASE:-https://api.openai.com/v1}"
    export LLM_API_KEY="${LLM_API_KEY:-$OPENAI_API_KEY}"
    export LLM_MODEL="${LLM_MODEL:-gpt-4o-mini}"
fi

export ENVIRONMENT="${ENVIRONMENT:-production}"
export RELEASE="${RELEASE:-1.0.0}"
export USER_RATE_LIMIT="${USER_RATE_LIMIT:-60}"

# PostgreSQL auto-config if individual vars are set but not DATABASE_URL
if [ -z "$DATABASE_URL" ] && [ -n "$POSTGRES_PASSWORD" ]; then
    export DATABASE_URL="postgresql://${POSTGRES_USER:-masterygraph}:${POSTGRES_PASSWORD}@${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-masterygraph}"
    echo "[DB] PostgreSQL: $DATABASE_URL" >&2
fi

exec /usr/bin/python3 -m uvicorn masterygraph_api:app --host 0.0.0.0 --port 8000
