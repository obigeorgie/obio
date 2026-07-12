#!/usr/bin/env python3
"""
MasteryGraph Core — API Key Manager
Per-user API keys stored in SQLite with generation, validation, and revocation.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import sqlite3
from contextlib import contextmanager

DB_PATH = Path("/root/.openclaw/workspace/masterygraph.db")

class APIKeyManager:
    """
    Manage per-user API keys with rate limiting and revocation.
    Keys are stored as SHA-256 hashes (never plaintext) for security.
    """
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_schema()
        # In-memory rate limit tracking: {key_hash: [(timestamp, count)]}
        self._rate_limits = defaultdict(list)
    
    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    @contextmanager
    def _transaction(self):
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS api_keys (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash    TEXT NOT NULL UNIQUE,
            name        TEXT,
            scopes      TEXT,  -- JSON array of allowed endpoints
            rate_limit  INTEGER DEFAULT 100,  -- requests per minute
            revoked     INTEGER DEFAULT 0,     -- 0 = active, 1 = revoked
            last_used   TEXT,
            created_at  TEXT NOT NULL,
            expires_at  TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
        CREATE INDEX IF NOT EXISTS idx_api_keys_revoked ON api_keys(revoked);
        """
        with self._transaction() as conn:
            conn.executescript(schema)
    
    def _hash(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    def generate_key(self, name=None, scopes=None, rate_limit=100, expires_days=None):
        """
        Generate a new API key. Returns the plaintext key (save it now — it's never shown again).
        """
        key = "mg_" + secrets.token_urlsafe(32)
        key_hash = self._hash(key)
        now = datetime.now().isoformat()
        expires = None
        if expires_days:
            expires = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO api_keys (key_hash, name, scopes, rate_limit, revoked, created_at, expires_at)
                VALUES (?, ?, ?, ?, 0, ?, ?)
                """,
                (key_hash, name, ",".join(scopes or ["*"]), rate_limit, now, expires),
            )
        return {
            "key": key,
            "name": name,
            "scopes": scopes or ["*"],
            "rate_limit": rate_limit,
            "expires_at": expires,
        }
    
    def validate_key(self, key: str):
        """
        Validate an API key. Returns dict with key info or None if invalid/revoked/expired.
        """
        key_hash = self._hash(key)
        with self._transaction() as conn:
            row = conn.execute(
                """
                SELECT * FROM api_keys 
                WHERE key_hash = ? AND revoked = 0
                """,
                (key_hash,),
            ).fetchone()
        
        if not row:
            return None
        
        # Check expiration
        if row["expires_at"] and datetime.now() > datetime.fromisoformat(row["expires_at"]):
            return None
        
        # Update last_used
        now = datetime.now().isoformat()
        with self._transaction() as conn:
            conn.execute(
                "UPDATE api_keys SET last_used = ? WHERE key_hash = ?",
                (now, key_hash),
            )
        
        return {
            "key_hash": row["key_hash"],
            "name": row["name"],
            "scopes": row["scopes"].split(",") if row["scopes"] else ["*"],
            "rate_limit": row["rate_limit"],
        }
    
    def check_rate_limit(self, key: str, window_seconds=60, max_requests=None):
        """
        Simple in-memory sliding window rate limit.
        Returns (allowed: bool, remaining: int, reset_in: int).
        """
        key_hash = self._hash(key)
        info = self.validate_key(key)
        if not info:
            return False, 0, 0
        
        max_req = max_requests or info["rate_limit"]
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old entries and count current window
        self._rate_limits[key_hash] = [
            t for t in self._rate_limits[key_hash] if t > window_start
        ]
        current_count = len(self._rate_limits[key_hash])
        
        if current_count >= max_req:
            reset_in = int((self._rate_limits[key_hash][0] - window_start).total_seconds())
            return False, 0, reset_in
        
        self._rate_limits[key_hash].append(now)
        remaining = max_req - current_count - 1
        return True, remaining, 0
    
    def revoke_key(self, key: str):
        """Revoke an API key."""
        key_hash = self._hash(key)
        with self._transaction() as conn:
            conn.execute(
                "UPDATE api_keys SET revoked = 1 WHERE key_hash = ?",
                (key_hash,),
            )
        return True
    
    def list_keys(self, include_revoked=False):
        """List all API keys."""
        with self._transaction() as conn:
            if include_revoked:
                rows = conn.execute(
                    "SELECT key_hash, name, scopes, rate_limit, revoked, last_used, created_at, expires_at FROM api_keys ORDER BY created_at DESC"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT key_hash, name, scopes, rate_limit, revoked, last_used, created_at, expires_at FROM api_keys WHERE revoked = 0 ORDER BY created_at DESC"
                ).fetchall()
        return [dict(r) for r in rows]
    
    def delete_key(self, key_hash: str):
        """Permanently delete a key."""
        with self._transaction() as conn:
            conn.execute("DELETE FROM api_keys WHERE key_hash = ?", (key_hash,))
        return True
    
    def get_stats(self):
        with self._transaction() as conn:
            total = conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM api_keys WHERE revoked = 0").fetchone()[0]
            revoked = conn.execute("SELECT COUNT(*) FROM api_keys WHERE revoked = 1").fetchone()[0]
        return {"total": total, "active": active, "revoked": revoked}

if __name__ == "__main__":
    mgr = APIKeyManager()
    
    print("=" * 60)
    print("MasteryGraph Core — API Key Manager")
    print("=" * 60)
    
    # Generate a key
    print("\n1. Generate new key")
    key_info = mgr.generate_key(
        name="Obioma Care Admin",
        scopes=["*"],
        rate_limit=1000,
        expires_days=365,
    )
    print(f"   Key: {key_info['key'][:20]}... (save this!)")
    print(f"   Name: {key_info['name']}")
    print(f"   Rate limit: {key_info['rate_limit']}/min")
    
    # Validate
    print("\n2. Validate key")
    validated = mgr.validate_key(key_info["key"])
    print(f"   Valid: {validated is not None}")
    print(f"   Scopes: {validated['scopes']}")
    
    # Rate limit check
    print("\n3. Rate limit check")
    allowed, remaining, reset = mgr.check_rate_limit(key_info["key"])
    print(f"   Allowed: {allowed}, Remaining: {remaining}")
    
    # List keys
    print("\n4. List keys")
    keys = mgr.list_keys()
    print(f"   Active keys: {len(keys)}")
    
    # Stats
    print("\n5. Stats")
    print(f"   {mgr.get_stats()}")
    
    # Cleanup (don't revoke the demo key so API stays working)
    print("\n✅ API Key Manager ready")
    print(f"   Add to API requests: X-API-Key: {key_info['key']}")
