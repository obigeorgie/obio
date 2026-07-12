# MasteryGraph — DNS Setup

## Architecture

| Subdomain | Target | Purpose |
|-----------|--------|---------|
| `api.obiomacare.com` | Cloudflare Tunnel → `localhost:8000` | FastAPI backend (HTTPS via Cloudflare) |
| `app.obiomacare.com` | `76.76.21.21` (A record) → Vercel | React frontend |

## DNS Records (Cloudflare)

```
Type: CNAME
Name: api
Target: <tunnel-id>.cfargotunnel.com
Proxied: Yes (orange cloud)
```

```
Type: A
Name: app
Value: 76.76.21.21
Proxied: No (gray cloud — Vercel handles SSL)
```

> Vercel requires the A record for `app`. Cloudflare handles SSL for `api` via the tunnel.

## Current Status

| Component | State |
|-----------|-------|
| FastAPI backend | ✅ Running on `localhost:8000` |
| Cloudflare Tunnel | ✅ Running, `masterygraph-api` tunnel active |
| Tunnel DNS route | ✅ CNAME `api.obiomacare.com` routed to tunnel |
| Vercel frontend | ✅ Deployed |
| Custom domain (app) | ✅ Live at `https://app.obiomacare.com` |
| API via tunnel | ✅ Verified working (direct Cloudflare IP test passed) |

## DNS Propagation Note

DNS is still propagating globally. Some resolvers may still return the old A record (`43.98.195.136`) for `api.obiomacare.com`. Full propagation typically takes 5–15 minutes.

**Test the tunnel directly:**
```bash
curl -s https://api.obiomacare.com/health
```

**With API key:**
```bash
curl -s -H "X-API-Key: mg_UiZrA-tJDRMWGKT23x_rz4z568Vusk-oOq3Yp_CuV2g" \
  https://api.obiomacare.com/v1/stats
```

## Vercel URLs

- Production: https://masterygraph-frontend.vercel.app
- Custom domain: https://app.obiomacare.com

## API Base URL

```
https://api.obiomacare.com/v1/
```

## Tested Endpoints

```bash
curl https://api.obiomacare.com/health
# → {"status":"healthy", ...}

curl -H "X-API-Key: mg_UiZrA-tJDRMWGKT23x_rz4z568Vusk-oOq3Yp_CuV2g" \
  https://api.obiomacare.com/v1/stats
# → {"learners":2, ...}
```

## Tunnel Service

```bash
systemctl status cloudflared
# Active: active (running)
```

Auto-starts on boot. No open ports required on the VPS.
