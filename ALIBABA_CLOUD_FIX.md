# OBIO API — HTTPS Setup Blocked by Alibaba Cloud Security Group

## Problem Identified

Your VPS is **Alibaba Cloud Singapore** (IP: 43.98.195.136). 

Caddy is running and listening on ports 80 and 443, but **Alibaba Cloud's security group (防火墙)** is blocking external access. This is why Let's Encrypt cannot reach your server to validate the SSL certificate.

Error from Let's Encrypt: `Timeout during connect (likely firewall problem)`

## What You Need to Do

Open ports **80** and **443** in your Alibaba Cloud Security Group:

### Step 1: Log into Alibaba Cloud Console
https://www.alibabacloud.com/

### Step 2: Navigate to Security Groups
- Go to **ECS Console** → **Network & Security** → **Security Groups**
- Find the security group attached to your instance (iZt4nd0arh0fmao60lxabvZ)

### Step 3: Add Inbound Rules

Add these 2 rules:

| Type | Protocol | Port Range | Source | Action | Priority |
|------|----------|------------|--------|--------|----------|
| Custom TCP | TCP | 80/80 | 0.0.0.0/0 | Allow | 1 |
| Custom TCP | TCP | 443/443 | 0.0.0.0/0 | Allow | 1 |

Or if using the Quick Rule templates:
- Select **HTTP (80)** → Allow → Source: 0.0.0.0/0
- Select **HTTPS (443)** → Allow → Source: 0.0.0.0/0

### Step 4: Apply & Wait
- Click **Save** or **Apply**
- Wait 1-2 minutes for rules to take effect

### Step 5: Verify

After opening the ports, run:
```bash
curl -v https://api.obiomacare.com/v1/health
```

Or tell me to run it and I'll confirm HTTPS is working.

## Current Status

| Component | Status |
|-----------|--------|
| FastAPI API | ✅ Running on port 8000 |
| Caddy Proxy | ✅ Running on ports 80/443 |
| DNS (api.obiomacare.com) | ✅ Resolving to 43.98.195.136 |
| Alibaba Cloud Security Group | ❌ Blocking ports 80/443 |
| SSL Certificate | ⏳ Waiting for port access |

## Alternative (Temporary)

If you can't access the Alibaba Cloud console right now, you can use the API via HTTP on port 80 (once ports are open) or access it directly via IP. But for HTTPS/auto-SSL, the security group rules must be opened.
