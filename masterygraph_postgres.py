#!/usr/bin/env python3
"""
MasteryGraph Core — PostgreSQL Persistence Layer
Production-ready database backend with connection pooling.
Drop-in replacement for masterygraph_db.py (SQLite).

Environment variables:
  DATABASE_URL — full PostgreSQL connection string
    e.g. "postgresql://masterygraph:mg_secure_pass_2024@localhost:5432/masterygraph"
  If not set, falls back to SQLite via masterygraph_db.py
"""

import json
import os
import logging
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict
from typing import Dict, List, Optional, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_values
    from psycopg2.pool import ThreadedConnectionPool
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "")

def _get_connection_url():
    """Build connection URL from DATABASE_URL or individual env vars."""
    if DATABASE_URL:
        return DATABASE_URL
    # Build from components
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "masterygraph")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    dbname = os.environ.get("POSTGRES_DB", "masterygraph")
    if not password:
        return None
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

# ---------------------------------------------------------------------------
# Schema (PostgreSQL-compatible)
# ---------------------------------------------------------------------------
POSTGRES_SCHEMA = """
-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Learners table
CREATE TABLE IF NOT EXISTS learners (
    id          TEXT PRIMARY KEY,
    name        TEXT,
    age         INTEGER,
    grade       TEXT,
    notes       TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Mastery map
CREATE TABLE IF NOT EXISTS mastery (
    id            SERIAL PRIMARY KEY,
    learner_id    TEXT NOT NULL,
    topic_id      TEXT NOT NULL,
    status        TEXT CHECK(status IN ('mastered','in-progress','not-started')),
    confidence    REAL,
    notes         TEXT,
    last_assessed TIMESTAMP,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(learner_id, topic_id)
);

-- Goals
CREATE TABLE IF NOT EXISTS goals (
    id                TEXT PRIMARY KEY,
    learner_id        TEXT NOT NULL,
    target_topic_ids  JSONB,
    deadline          TIMESTAMP,
    notes             TEXT,
    status            TEXT CHECK(status IN ('active','completed','archived')) DEFAULT 'active',
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Diagnostics history
CREATE TABLE IF NOT EXISTS diagnostics (
    id          SERIAL PRIMARY KEY,
    learner_id  TEXT NOT NULL,
    topic_id    TEXT,
    format      TEXT,
    results     JSONB,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Learning paths history
CREATE TABLE IF NOT EXISTS learning_paths (
    id          SERIAL PRIMARY KEY,
    learner_id  TEXT NOT NULL,
    path_json   JSONB,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- System events log
CREATE TABLE IF NOT EXISTS system_logs (
    id          SERIAL PRIMARY KEY,
    event_type  TEXT NOT NULL,
    data        JSONB,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Users table (parent/teacher accounts)
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name          TEXT,
    role          TEXT CHECK(role IN ('parent','teacher','admin')) DEFAULT 'parent',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login    TIMESTAMP
);

-- Subscriptions (Stripe billing tracking)
CREATE TABLE IF NOT EXISTS subscriptions (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL,
    stripe_subscription_id TEXT UNIQUE,
    stripe_customer_id  TEXT,
    plan                TEXT CHECK(plan IN ('family','educator','free')) DEFAULT 'free',
    status              TEXT CHECK(status IN ('active','cancelled','past_due','unpaid','free')) DEFAULT 'free',
    current_period_end  BIGINT,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- User-Learner relationships
CREATE TABLE IF NOT EXISTS user_learners (
    user_id     TEXT NOT NULL,
    learner_id  TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, learner_id)
);

-- Audit logs (from audit_logger.py)
CREATE TABLE IF NOT EXISTS audit_logs (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type  TEXT NOT NULL,
    user_id     TEXT,
    ip_address  TEXT,
    resource    TEXT,
    action      TEXT,
    status      TEXT,
    details     JSONB,
    severity    TEXT CHECK(severity IN ('info','warning','error','critical')) DEFAULT 'info'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_mastery_learner     ON mastery(learner_id);
CREATE INDEX IF NOT EXISTS idx_mastery_topic       ON mastery(topic_id);
CREATE INDEX IF NOT EXISTS idx_mastery_status      ON mastery(learner_id, status);
CREATE INDEX IF NOT EXISTS idx_goals_learner       ON goals(learner_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_learner ON diagnostics(learner_id);
CREATE INDEX IF NOT EXISTS idx_logs_type           ON system_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_logs_time           ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_learners_user ON user_learners(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_time ON audit_logs(timestamp);

-- Trigger to auto-update updated_at on learners
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_learners_updated_at ON learners;
CREATE TRIGGER update_learners_updated_at
    BEFORE UPDATE ON learners
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mastery_updated_at ON mastery;
CREATE TRIGGER update_mastery_updated_at
    BEFORE UPDATE ON mastery
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

# ---------------------------------------------------------------------------
# PostgreSQL Database Manager
# ---------------------------------------------------------------------------
class MasteryGraphPostgresDB:
    """
    PostgreSQL-backed persistence for MasteryGraph Core.
    Drop-in replacement for MasteryGraphDB (SQLite).
    """

    def __init__(self, connection_url=None):
        self.connection_url = connection_url or _get_connection_url()
        if not self.connection_url:
            raise RuntimeError("No PostgreSQL connection URL configured. Set DATABASE_URL or POSTGRES_* env vars.")
        self._pool = None
        self._init_pool()
        self._init_schema()

    def _init_pool(self):
        """Initialize threaded connection pool."""
        try:
            self._pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                dsn=self.connection_url,
                cursor_factory=RealDictCursor
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def _init_schema(self):
        """Create tables and indexes."""
        with self._transaction() as cur:
            cur.execute(POSTGRES_SCHEMA)

    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        conn = self._pool.getconn()
        try:
            cur = conn.cursor()
            yield cur
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            self._pool.putconn(conn)

    @contextmanager
    def _connection(self):
        """Context manager for read-only connections."""
        conn = self._pool.getconn()
        try:
            cur = conn.cursor()
            yield cur
        finally:
            if cur:
                cur.close()
            self._pool.putconn(conn)

    # ── Learners ───────────────────────────────────────────────────────
    def create_learner(self, learner_id: str, name: str, age: int = None, grade: str = None, notes: str = ""):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO learners (id, name, age, grade, notes, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (learner_id, name, age, grade, notes, now, now)
            )
        return {"id": learner_id, "name": name, "age": age, "grade": grade, "notes": notes, "created_at": now, "updated_at": now}

    def get_learner(self, learner_id: str) -> Optional[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM learners WHERE id = %s", (learner_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def list_learners(self) -> List[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM learners ORDER BY created_at DESC")
            return [dict(row) for row in cur.fetchall()]

    def update_learner(self, learner_id: str, **fields):
        allowed = {"name", "age", "grade", "notes"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [learner_id]
        with self._transaction() as cur:
            cur.execute(f"UPDATE learners SET {set_clause} WHERE id = %s", values)
            return cur.rowcount > 0

    def delete_learner(self, learner_id: str):
        with self._transaction() as cur:
            cur.execute("DELETE FROM mastery WHERE learner_id = %s", (learner_id,))
            cur.execute("DELETE FROM goals WHERE learner_id = %s", (learner_id,))
            cur.execute("DELETE FROM diagnostics WHERE learner_id = %s", (learner_id,))
            cur.execute("DELETE FROM learning_paths WHERE learner_id = %s", (learner_id,))
            cur.execute("DELETE FROM user_learners WHERE learner_id = %s", (learner_id,))
            cur.execute("DELETE FROM learners WHERE id = %s", (learner_id,))
            return cur.rowcount > 0

    # ── Mastery ────────────────────────────────────────────────────────
    def update_mastery(self, learner_id: str, topic_id: str, status: str, confidence: float = None, notes: str = None):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                """INSERT INTO mastery (learner_id, topic_id, status, confidence, notes, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (learner_id, topic_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    confidence = EXCLUDED.confidence,
                    notes = EXCLUDED.notes,
                    updated_at = EXCLUDED.updated_at
                """,
                (learner_id, topic_id, status, confidence, notes, now, now)
            )
        return {"learner_id": learner_id, "topic_id": topic_id, "status": status, "confidence": confidence, "notes": notes, "updated_at": now}

    def get_all_mastery(self, learner_id: str) -> Dict[str, Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM mastery WHERE learner_id = %s", (learner_id,))
            rows = cur.fetchall()
            return {row["topic_id"]: dict(row) for row in rows}

    def get_mastery_by_status(self, learner_id: str, status: str) -> List[str]:
        with self._connection() as cur:
            cur.execute("SELECT topic_id FROM mastery WHERE learner_id = %s AND status = %s", (learner_id, status))
            return [row["topic_id"] for row in cur.fetchall()]

    def bulk_update_mastery(self, learner_id: str, updates: List[Dict]):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            for u in updates:
                cur.execute(
                    """INSERT INTO mastery (learner_id, topic_id, status, confidence, notes, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (learner_id, topic_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        confidence = EXCLUDED.confidence,
                        notes = EXCLUDED.notes,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (learner_id, u["topic_id"], u["status"], u.get("confidence"), u.get("notes"), now, now)
                )
        return {"learner_id": learner_id, "updated_count": len(updates)}

    # ── Goals ──────────────────────────────────────────────────────────
    def create_goal(self, goal_id: str, learner_id: str, target_topic_ids: List[str], deadline: str = None, notes: str = ""):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO goals (id, learner_id, target_topic_ids, deadline, notes, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (goal_id, learner_id, json.dumps(target_topic_ids), deadline, notes, "active", now)
            )
        return {"id": goal_id, "learner_id": learner_id, "target_topic_ids": target_topic_ids, "deadline": deadline, "notes": notes, "status": "active", "created_at": now}

    def get_goals(self, learner_id: str) -> List[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM goals WHERE learner_id = %s ORDER BY created_at DESC", (learner_id,))
            rows = cur.fetchall()
            for row in rows:
                row["target_topic_ids"] = json.loads(row["target_topic_ids"]) if row["target_topic_ids"] else []
            return [dict(row) for row in rows]

    def update_goal_status(self, goal_id: str, status: str):
        with self._transaction() as cur:
            cur.execute("UPDATE goals SET status = %s WHERE id = %s", (status, goal_id))
            return cur.rowcount > 0

    # ── Diagnostics ────────────────────────────────────────────────────
    def log_diagnostic(self, learner_id: str, topic_id: str = None, format: str = None, results: Dict = None):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO diagnostics (learner_id, topic_id, format, results, created_at) VALUES (%s, %s, %s, %s, %s)",
                (learner_id, topic_id, format, json.dumps(results) if results else None, now)
            )
        return {"id": cur.fetchone()["id"] if False else None, "learner_id": learner_id, "topic_id": topic_id, "format": format, "created_at": now}

    def get_diagnostics(self, learner_id: str, limit: int = 50) -> List[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM diagnostics WHERE learner_id = %s ORDER BY created_at DESC LIMIT %s", (learner_id, limit))
            rows = cur.fetchall()
            for row in rows:
                if row["results"]:
                    row["results"] = json.loads(row["results"])
            return [dict(row) for row in rows]

    # ── Learning Paths ───────────────────────────────────────────────
    def save_learning_path(self, learner_id: str, path: List[Dict]):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO learning_paths (learner_id, path_json, created_at) VALUES (%s, %s, %s)",
                (learner_id, json.dumps(path), now)
            )
        return {"learner_id": learner_id, "path": path, "created_at": now}

    def get_learning_paths(self, learner_id: str, limit: int = 10) -> List[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM learning_paths WHERE learner_id = %s ORDER BY created_at DESC LIMIT %s", (learner_id, limit))
            rows = cur.fetchall()
            for row in rows:
                row["path_json"] = json.loads(row["path_json"]) if row["path_json"] else []
            return [dict(row) for row in rows]

    # ── System Logs ──────────────────────────────────────────────────
    def log_event(self, event_type: str, data: Dict = None):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO system_logs (event_type, data, created_at) VALUES (%s, %s, %s)",
                (event_type, json.dumps(data) if data else None, now)
            )
        return {"event_type": event_type, "data": data, "created_at": now}

    def get_logs(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        with self._connection() as cur:
            if event_type:
                cur.execute("SELECT * FROM system_logs WHERE event_type = %s ORDER BY created_at DESC LIMIT %s", (event_type, limit))
            else:
                cur.execute("SELECT * FROM system_logs ORDER BY created_at DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
            for row in rows:
                if row["data"]:
                    row["data"] = json.loads(row["data"])
            return [dict(row) for row in rows]

    # ── Users ──────────────────────────────────────────────────────────
    def create_user(self, user_id: str, email: str, password_hash: str, name: str = None, role: str = "parent"):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO users (id, email, password_hash, name, role, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_id, email.lower(), password_hash, name, role, now, now)
            )
        return {"id": user_id, "email": email.lower(), "name": name, "role": role, "created_at": now, "updated_at": now}

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_user(self, user_id: str, **fields):
        allowed = {"name", "password_hash", "role", "last_login"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        with self._transaction() as cur:
            cur.execute(f"UPDATE users SET {set_clause} WHERE id = %s", values)
            return cur.rowcount > 0

    # ── Subscriptions ────────────────────────────────────────────────
    def create_subscription(self, sub_id: str, user_id: str, plan: str = "free", status: str = "free"):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO subscriptions (id, user_id, plan, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (sub_id, user_id, plan, status, now, now)
            )
        return {"id": sub_id, "user_id": user_id, "plan": plan, "status": status, "created_at": now, "updated_at": now}

    def get_subscription(self, user_id: str) -> Optional[Dict]:
        with self._connection() as cur:
            cur.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_subscription(self, user_id: str, **fields):
        allowed = {"plan", "status", "stripe_subscription_id", "stripe_customer_id", "current_period_end", "cancel_at_period_end"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        with self._transaction() as cur:
            cur.execute(f"UPDATE subscriptions SET {set_clause} WHERE user_id = %s", values)
            return cur.rowcount > 0

    # ── User-Learner Links ───────────────────────────────────────────
    def link_user_learner(self, user_id: str, learner_id: str):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO user_learners (user_id, learner_id, created_at) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (user_id, learner_id, now)
            )
        return {"user_id": user_id, "learner_id": learner_id, "created_at": now}

    def get_user_learners(self, user_id: str) -> List[str]:
        with self._connection() as cur:
            cur.execute("SELECT learner_id FROM user_learners WHERE user_id = %s", (user_id,))
            return [row["learner_id"] for row in cur.fetchall()]

    def unlink_user_learner(self, user_id: str, learner_id: str):
        with self._transaction() as cur:
            cur.execute("DELETE FROM user_learners WHERE user_id = %s AND learner_id = %s", (user_id, learner_id))
            return cur.rowcount > 0

    # ── Audit Logs ───────────────────────────────────────────────────
    def log_audit(self, event_type: str, user_id: str = None, ip_address: str = None,
                  resource: str = None, action: str = None, status: str = None,
                  details: Dict = None, severity: str = "info"):
        now = datetime.utcnow().isoformat()
        with self._transaction() as cur:
            cur.execute(
                "INSERT INTO audit_logs (timestamp, event_type, user_id, ip_address, resource, action, status, details, severity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (now, event_type, user_id, ip_address, resource, action, status, json.dumps(details) if details else None, severity)
            )
        return {"id": cur.lastrowid if hasattr(cur, 'lastrowid') else None, "event_type": event_type, "timestamp": now}

    def get_audit_logs(self, user_id: str = None, event_type: str = None, limit: int = 100) -> List[Dict]:
        with self._connection() as cur:
            if user_id and event_type:
                cur.execute("SELECT * FROM audit_logs WHERE user_id = %s AND event_type = %s ORDER BY timestamp DESC LIMIT %s", (user_id, event_type, limit))
            elif user_id:
                cur.execute("SELECT * FROM audit_logs WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s", (user_id, limit))
            elif event_type:
                cur.execute("SELECT * FROM audit_logs WHERE event_type = %s ORDER BY timestamp DESC LIMIT %s", (event_type, limit))
            else:
                cur.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
            for row in rows:
                if row["details"]:
                    row["details"] = json.loads(row["details"])
            return [dict(row) for row in rows]

    # ── Stats ─────────────────────────────────────────────────────────
    def get_stats(self) -> Dict:
        with self._connection() as cur:
            cur.execute("SELECT COUNT(*) as count FROM learners")
            learners = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM mastery")
            mastery_entries = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM mastery WHERE status = 'mastered'")
            mastered_count = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM goals")
            goals = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM diagnostics")
            diagnostics = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM system_logs")
            system_logs = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM users")
            users = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) as count FROM subscriptions WHERE status = 'active'")
            active_subs = cur.fetchone()["count"]
            return {
                "learners": learners,
                "masteryEntries": mastery_entries,
                "masteredCount": mastered_count,
                "goals": goals,
                "diagnostics": diagnostics,
                "systemLogs": system_logs,
                "users": users,
                "activeSubscriptions": active_subs
            }

    # ── Cleanup ───────────────────────────────────────────────────────
    def close(self):
        if self._pool:
            self._pool.closeall()
            logger.info("PostgreSQL connection pool closed")


# ---------------------------------------------------------------------------
# Factory — auto-select based on DATABASE_URL
# ---------------------------------------------------------------------------
def get_db():
    """Return the appropriate database instance."""
    if _get_connection_url() and HAS_POSTGRES:
        return MasteryGraphPostgresDB()
    else:
        # Fall back to SQLite
        from masterygraph_db import MasteryGraphDB
        return MasteryGraphDB()


# ---------------------------------------------------------------------------
# Compatibility alias — same class name as SQLite version
# ---------------------------------------------------------------------------
class MasteryGraphDB(MasteryGraphPostgresDB):
    """Alias for drop-in compatibility."""
    pass
