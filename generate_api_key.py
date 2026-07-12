#!/usr/bin/env python3
"""Generate the production API key for MasteryGraph."""

from api_key_manager import APIKeyManager

mgr = APIKeyManager()

# Generate production key
key_info = mgr.generate_key(
    name="Obioma Care Production",
    scopes=["*"],
    rate_limit=1000,
    expires_days=365,
)

print("=" * 60)
print("PRODUCTION API KEY — SAVE THIS SECURELY")
print("=" * 60)
print(f"\n{key_info['key']}")
print(f"\nName: {key_info['name']}")
print(f"Rate limit: {key_info['rate_limit']}/min")
print(f"Expires: {key_info['expires_at']}")
print(f"\nAdd to requests: X-API-Key: {key_info['key']}")
print(f"\n⚠️  This key is shown only once. Store it in your password manager.")
