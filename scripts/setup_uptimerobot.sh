#!/bin/bash
# MasteryGraph UptimeRobot Monitor Setup
# Run this script after obtaining your UptimeRobot API key
# Get your API key at: https://uptimerobot.com/dashboard -> Integrations & API

set -euo pipefail

UPTIMEROBOT_API_KEY="${UPTIMEROBOT_API_KEY:-}"

if [ -z "$UPTIMEROBOT_API_KEY" ]; then
    echo "ERROR: Set UPTIMEROBOT_API_KEY environment variable"
    echo "Get your key at: https://uptimerobot.com/dashboard -> Integrations & API"
    exit 1
fi

echo "=== Creating UptimeRobot Monitors ==="

# Monitor 1: API Health
echo "Creating: OBIO API Health..."
curl -s -X POST https://api.uptimerobot.com/v2/newMonitor \
    -d "api_key=$UPTIMEROBOT_API_KEY" \
    -d "format=json" \
    -d "type=1" \
    -d "url=https://api.obiomacare.com/v1/health" \
    -d "friendly_name=OBIO API Health" \
    -d "interval=300" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ID:', d.get('monitor', {}).get('id'), 'Status:', d.get('stat'))"

# Monitor 2: Frontend App
echo "Creating: OBIO App (app.obiomacare.com)..."
curl -s -X POST https://api.uptimerobot.com/v2/newMonitor \
    -d "api_key=$UPTIMEROBOT_API_KEY" \
    -d "format=json" \
    -d "type=1" \
    -d "url=https://app.obiomacare.com" \
    -d "friendly_name=OBIO App" \
    -d "interval=300" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ID:', d.get('monitor', {}).get('id'), 'Status:', d.get('stat'))"

# Monitor 3: Landing Page
echo "Creating: OBIO Landing (obiomacare.com)..."
curl -s -X POST https://api.uptimerobot.com/v2/newMonitor \
    -d "api_key=$UPTIMEROBOT_API_KEY" \
    -d "format=json" \
    -d "type=1" \
    -d "url=https://obiomacare.com" \
    -d "friendly_name=OBIO Landing Page" \
    -d "interval=300" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ID:', d.get('monitor', {}).get('id'), 'Status:', d.get('stat'))"

# Monitor 4: Stripe Checkout (critical payment path)
echo "Creating: OBIO Stripe Checkout..."
curl -s -X POST https://api.uptimerobot.com/v2/newMonitor \
    -d "api_key=$UPTIMEROBOT_API_KEY" \
    -d "format=json" \
    -d "type=1" \
    -d "url=https://api.obiomacare.com/v1/pricing" \
    -d "friendly_name=OBIO Pricing API" \
    -d "interval=300" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ID:', d.get('monitor', {}).get('id'), 'Status:', d.get('stat'))"

echo ""
echo "=== Setup Complete ==="
echo "Dashboard: https://uptimerobot.com/dashboard"
echo ""
echo "Monitors check every 5 minutes (300 seconds)"
echo "You'll get email alerts if any endpoint goes down."
