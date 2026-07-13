#!/bin/bash
# Start the OBIO backend
# REQUIRED: Set these environment variables before running:
#   export RESEND_API_KEY="..."
#   export RESEND_FROM_EMAIL="OBIO <admin@obiomacare.com>"
#   export OPENAI_API_KEY="..."
#   export STRIPE_SECRET_KEY="..."
#   export STRIPE_WEBHOOK_SECRET="..."
#   export SENTRY_DSN="..."  (optional)
#
# Set them in ~/.bashrc, /etc/environment, or a .env file (gitignored)

cd /root/.openclaw/workspace

# Validate required env vars
MISSING=0
for VAR in RESEND_API_KEY RESEND_FROM_EMAIL OPENAI_API_KEY STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET; do
    if [ -z "${!VAR}" ]; then
        echo "ERROR: $VAR is not set" >&2
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "Set required env vars and try again." >&2
    exit 1
fi

# Optional: derive LLM_API_KEY from OPENAI if not set
export LLM_API_KEY="${LLM_API_KEY:-$OPENAI_API_KEY}"

# Defaults
export LLM_API_BASE="${LLM_API_BASE:-https://api.openai.com/v1}"
export LLM_MODEL="${LLM_MODEL:-gpt-4o-mini}"
export ENVIRONMENT="${ENVIRONMENT:-production}"
export RELEASE="${RELEASE:-1.0.0}"
export USER_RATE_LIMIT="${USER_RATE_LIMIT:-60}"

exec /usr/bin/python3 -m uvicorn masterygraph_api:app --host 0.0.0.0 --port 8000
