#!/usr/bin/env python3
"""
MasteryGraph Auth — JWT-based authentication for parents/teachers.
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from pathlib import Path

# In production, load from env var
JWT_SECRET = "masterygraph-dev-secret-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30

DB_PATH = Path("/root/.openclaw/workspace/masterygraph.db")

class AuthManager:
    """Handles user registration, login, and JWT management."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure tables exist (called once)."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id            TEXT PRIMARY KEY,
                    email         TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name          TEXT,
                    role          TEXT DEFAULT 'parent',
                    created_at    TEXT NOT NULL,
                    updated_at    TEXT NOT NULL,
                    last_login    TEXT
                );
                CREATE TABLE IF NOT EXISTS user_learners (
                    user_id     TEXT NOT NULL,
                    learner_id  TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    PRIMARY KEY (user_id, learner_id)
                );
                CREATE TABLE IF NOT EXISTS password_resets (
                    id          TEXT PRIMARY KEY,
                    user_id     TEXT NOT NULL,
                    token       TEXT UNIQUE NOT NULL,
                    expires_at  TEXT NOT NULL,
                    used        INTEGER DEFAULT 0,
                    created_at  TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_user_learners_user ON user_learners(user_id);
                CREATE INDEX IF NOT EXISTS idx_password_resets_token ON password_resets(token);
            """)
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + pwdhash.hex()
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        salt = stored_hash[:32]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwdhash.hex() == stored_hash[32:]
    
    def register(self, email: str, password: str, name: str = None, role: str = "parent") -> Dict[str, Any]:
        """Register a new user. Returns user data or raises ValueError."""
        import sqlite3
        user_id = f"usr_{uuid.uuid4().hex[:16]}"
        now = datetime.utcnow().isoformat()
        password_hash = self._hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """INSERT INTO users (id, email, password_hash, name, role, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, email.lower(), password_hash, name, role, now, now)
                )
                # Create default free subscription
                conn.execute(
                    """INSERT INTO subscriptions (id, user_id, plan, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (f"sub_{user_id}", user_id, "free", "free", now, now)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError("Email already registered")
        
        return {"id": user_id, "email": email.lower(), "name": name, "role": role}
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return JWT token."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, password_hash, name, role FROM users WHERE email = ?",
                (email.lower(),)
            ).fetchone()
        
        if not row:
            raise ValueError("Invalid email or password")
        
        user_id, stored_hash, name, role = row
        if not self._verify_password(password, stored_hash):
            raise ValueError("Invalid email or password")
        
        # Update last login
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
            conn.commit()
        
        # Generate JWT
        token = self._create_token(user_id, email.lower(), role)
        
        return {
            "token": token,
            "user": {"id": user_id, "email": email.lower(), "name": name, "role": role}
        }
    
    def _create_token(self, user_id: str, email: str, role: str) -> str:
        """Create JWT token."""
        expires = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expires,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def generate_reset_token(self, email: str) -> str:
        """Generate a password reset token. Returns token or raises ValueError."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT id FROM users WHERE email = ?", (email.lower(),)).fetchone()
            if not row:
                raise ValueError("Email not found")
            user_id = row[0]
            
            # Invalidate old tokens
            conn.execute("UPDATE password_resets SET used = 1 WHERE user_id = ?", (user_id,))
            
            token = secrets.token_urlsafe(32)
            now = datetime.utcnow()
            expires = (now + timedelta(hours=24)).isoformat()
            conn.execute(
                """INSERT INTO password_resets (id, user_id, token, expires_at, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (f"rst_{uuid.uuid4().hex[:16]}", user_id, token, expires, now.isoformat())
            )
            conn.commit()
        return token
    
    def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify a reset token and return user_id."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT user_id, expires_at, used FROM password_resets WHERE token = ?""",
                (token,)
            ).fetchone()
            if not row:
                return None
            user_id, expires_at, used = row
            if used:
                return None
            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                return None
            return user_id
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token."""
        import sqlite3
        user_id = self.verify_reset_token(token)
        if not user_id:
            return False
        
        password_hash = self._hash_password(new_password)
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (password_hash, now, user_id)
            )
            conn.execute(
                "UPDATE password_resets SET used = 1 WHERE token = ?",
                (token,)
            )
            conn.commit()
        return True
    
    def update_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Update password with current password verification."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            if not row:
                return False
            if not self._verify_password(current_password, row[0]):
                return False
            
            password_hash = self._hash_password(new_password)
            now = datetime.utcnow().isoformat()
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (password_hash, now, user_id)
            )
            conn.commit()
        return True
    
    def update_profile(self, user_id: str, name: str = None, email: str = None) -> bool:
        """Update user profile."""
        import sqlite3
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            if name and email:
                conn.execute(
                    "UPDATE users SET name = ?, email = ?, updated_at = ? WHERE id = ?",
                    (name, email.lower(), now, user_id)
                )
            elif name:
                conn.execute(
                    "UPDATE users SET name = ?, updated_at = ? WHERE id = ?",
                    (name, now, user_id)
                )
            elif email:
                conn.execute(
                    "UPDATE users SET email = ?, updated_at = ? WHERE id = ?",
                    (email.lower(), now, user_id)
                )
            conn.commit()
        return True

    def get_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user subscription."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT plan, status, stripe_subscription_id, current_period_end, cancel_at_period_end
                   FROM subscriptions WHERE user_id = ?""",
                (user_id,)
            ).fetchone()
        if not row:
            return None
        return {
            "plan": row[0],
            "status": row[1],
            "stripe_subscription_id": row[2],
            "current_period_end": row[3],
            "cancel_at_period_end": bool(row[4]),
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {
                "id": payload["sub"],
                "email": payload["email"],
                "role": payload["role"],
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, email, name, role, created_at, last_login FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "role": row[3],
            "created_at": row[4],
            "last_login": row[5],
        }
    
    def link_learner(self, user_id: str, learner_id: str) -> bool:
        """Link a learner to a user (parent)."""
        import sqlite3
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO user_learners (user_id, learner_id, created_at) VALUES (?, ?, ?)",
                    (user_id, learner_id, now)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Already linked
    
    def get_user_learners(self, user_id: str) -> list:
        """Get all learners linked to a user."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT learner_id FROM user_learners WHERE user_id = ?",
                (user_id,)
            ).fetchall()
        return [r[0] for r in rows]
