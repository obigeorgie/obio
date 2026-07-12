#!/usr/bin/env python3
"""
MasteryGraph Core — SQLite Persistence Layer
Clean database backend for learner profiles, mastery maps, goals, diagnostics,
and system logs. Drop-in compatible with the existing JSON profile structure.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DB_PATH = Path("/root/.openclaw/workspace/masterygraph.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
SCHEMA = """
-- Learners table (replaces JSON profile metadata)
CREATE TABLE IF NOT EXISTS learners (
    id          TEXT PRIMARY KEY,
    name        TEXT,
    age         INTEGER,
    grade       TEXT,
    notes       TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- Mastery map (replaces profile.masteryMap)
CREATE TABLE IF NOT EXISTS mastery (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id    TEXT NOT NULL,
    topic_id      TEXT NOT NULL,
    status        TEXT CHECK(status IN ('mastered','in-progress','not-started')),
    confidence    REAL,
    notes         TEXT,
    last_assessed TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    UNIQUE(learner_id, topic_id)
);

-- Goals (replaces profile.goals)
CREATE TABLE IF NOT EXISTS goals (
    id                TEXT PRIMARY KEY,
    learner_id        TEXT NOT NULL,
    target_topic_ids  TEXT,   -- JSON array
    deadline          TEXT,
    notes             TEXT,
    status            TEXT CHECK(status IN ('active','completed','archived')),
    created_at        TEXT NOT NULL
);

-- Diagnostics history (replaces profile.diagnostics)
CREATE TABLE IF NOT EXISTS diagnostics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id  TEXT NOT NULL,
    topic_id    TEXT,
    format      TEXT,
    results     TEXT,   -- JSON
    created_at  TEXT NOT NULL
);

-- Learning paths history (replaces profile.learningPaths)
CREATE TABLE IF NOT EXISTS learning_paths (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id  TEXT NOT NULL,
    path_json   TEXT,   -- JSON
    created_at  TEXT NOT NULL
);

-- System events log (replaces JSONL logs)
CREATE TABLE IF NOT EXISTS system_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    data        TEXT,   -- JSON
    created_at  TEXT NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_mastery_learner     ON mastery(learner_id);
CREATE INDEX IF NOT EXISTS idx_mastery_topic       ON mastery(topic_id);
CREATE INDEX IF NOT EXISTS idx_mastery_status      ON mastery(learner_id, status);
CREATE INDEX IF NOT EXISTS idx_goals_learner       ON goals(learner_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_learner ON diagnostics(learner_id);
CREATE INDEX IF NOT EXISTS idx_logs_type           ON system_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_logs_time           ON system_logs(created_at);

-- Users table (parent/teacher accounts)
CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    email        TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name         TEXT,
    role         TEXT CHECK(role IN ('parent','teacher','admin')) DEFAULT 'parent',
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    last_login   TEXT
);

-- Subscriptions (Stripe billing tracking)
CREATE TABLE IF NOT EXISTS subscriptions (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL,
    stripe_subscription_id TEXT UNIQUE,
    stripe_customer_id  TEXT,
    plan                TEXT CHECK(plan IN ('family','educator','free')) DEFAULT 'free',
    status              TEXT CHECK(status IN ('active','cancelled','past_due','unpaid')) DEFAULT 'free',
    current_period_end  INTEGER,
    cancel_at_period_end INTEGER DEFAULT 0,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);

-- User-Learner relationships (one parent can have multiple children)
CREATE TABLE IF NOT EXISTS user_learners (
    user_id     TEXT NOT NULL,
    learner_id  TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    PRIMARY KEY (user_id, learner_id)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_learners_user ON user_learners(user_id);
"""

# ---------------------------------------------------------------------------
# Database Manager
# ---------------------------------------------------------------------------
class MasteryGraphDB:
    """
    SQLite-backed persistence for MasteryGraph Core.
    Mirrors the JSON profile structure from update_learner_profile.py.
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_schema()

    # ── Connection helpers ──────────────────────────────────────────────
    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
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
        with self._transaction() as conn:
            conn.executescript(SCHEMA)

    def _now(self):
        return datetime.now().isoformat()

    # ── Learners ────────────────────────────────────────────────────────
    def create_learner(self, learner_id, name=None, age=None, grade=None, notes=""):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO learners (id, name, age, grade, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name, age=excluded.age, grade=excluded.grade,
                    notes=excluded.notes, updated_at=excluded.updated_at
                """,
                (learner_id, name, age, grade, notes, now, now),
            )
        return self.get_learner(learner_id)

    def get_learner(self, learner_id):
        with self._transaction() as conn:
            row = conn.execute(
                "SELECT * FROM learners WHERE id = ?", (learner_id,)
            ).fetchone()
        if not row:
            return None
        return dict(row)

    def update_learner(self, learner_id, **fields):
        allowed = {"name", "age", "grade", "notes"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_learner(learner_id)
        cols = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [self._now(), learner_id]
        with self._transaction() as conn:
            conn.execute(
                f"UPDATE learners SET {cols}, updated_at = ? WHERE id = ?",
                vals,
            )
        return self.get_learner(learner_id)

    def list_learners(self):
        with self._transaction() as conn:
            rows = conn.execute("SELECT id, name, age, grade FROM learners").fetchall()
        return [dict(r) for r in rows]

    def delete_learner(self, learner_id):
        with self._transaction() as conn:
            conn.execute("DELETE FROM learners WHERE id = ?", (learner_id,))
            conn.execute("DELETE FROM mastery WHERE learner_id = ?", (learner_id,))
            conn.execute("DELETE FROM goals WHERE learner_id = ?", (learner_id,))
            conn.execute("DELETE FROM diagnostics WHERE learner_id = ?", (learner_id,))
            conn.execute("DELETE FROM learning_paths WHERE learner_id = ?", (learner_id,))
        return True

    # ── Mastery Map ─────────────────────────────────────────────────────
    def update_mastery(self, learner_id, topic_id, status, confidence=None, notes=""):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO mastery (learner_id, topic_id, status, confidence, notes, last_assessed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, topic_id) DO UPDATE SET
                    status=excluded.status,
                    confidence=excluded.confidence,
                    notes=excluded.notes,
                    last_assessed=excluded.last_assessed,
                    updated_at=excluded.updated_at
                """,
                (learner_id, topic_id, status, confidence, notes, now, now, now),
            )
        return self.get_mastery(learner_id, topic_id)

    def bulk_update_mastery(self, learner_id, updates):
        """
        updates: list of dicts {topicId, status, confidence?, notes?}
        """
        now = self._now()
        with self._transaction() as conn:
            for u in updates:
                conn.execute(
                    """
                    INSERT INTO mastery (learner_id, topic_id, status, confidence, notes, last_assessed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(learner_id, topic_id) DO UPDATE SET
                        status=excluded.status,
                        confidence=excluded.confidence,
                        notes=excluded.notes,
                        last_assessed=excluded.last_assessed,
                        updated_at=excluded.updated_at
                    """,
                    (learner_id, u["topicId"], u.get("status", "not-started"),
                     u.get("confidence"), u.get("notes", ""), now, now, now),
                )
        return self.get_all_mastery(learner_id)

    def get_mastery(self, learner_id, topic_id):
        with self._transaction() as conn:
            row = conn.execute(
                "SELECT * FROM mastery WHERE learner_id = ? AND topic_id = ?",
                (learner_id, topic_id),
            ).fetchone()
        if not row:
            return {"status": "not-started"}
        return dict(row)

    def get_all_mastery(self, learner_id):
        """Return full mastery map for a learner."""
        with self._transaction() as conn:
            rows = conn.execute(
                "SELECT topic_id, status, confidence, notes, last_assessed FROM mastery WHERE learner_id = ?",
                (learner_id,),
            ).fetchall()
        return {r["topic_id"]: dict(r) for r in rows}

    def get_mastery_by_status(self, learner_id, status):
        with self._transaction() as conn:
            rows = conn.execute(
                "SELECT topic_id FROM mastery WHERE learner_id = ? AND status = ?",
                (learner_id, status),
            ).fetchall()
        return [r["topic_id"] for r in rows]

    # ── Goals ────────────────────────────────────────────────────────────
    def add_goal(self, learner_id, target_topic_ids, deadline=None, notes="", status="active"):
        goal_id = f"goal_{self._now().replace(':', '-')}"
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO goals (id, learner_id, target_topic_ids, deadline, notes, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (goal_id, learner_id, json.dumps(target_topic_ids), deadline, notes, status, now),
            )
        return goal_id

    def get_goals(self, learner_id, status=None):
        with self._transaction() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM goals WHERE learner_id = ? AND status = ?",
                    (learner_id, status),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM goals WHERE learner_id = ?", (learner_id,)
                ).fetchall()
        goals = []
        for r in rows:
            d = dict(r)
            d["target_topic_ids"] = json.loads(d.get("target_topic_ids", "[]"))
            goals.append(d)
        return goals

    def update_goal_status(self, goal_id, status):
        with self._transaction() as conn:
            conn.execute(
                "UPDATE goals SET status = ? WHERE id = ?", (status, goal_id)
            )

    # ── Diagnostics ──────────────────────────────────────────────────────
    def log_diagnostic(self, learner_id, topic_id, format_type, results):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO diagnostics (learner_id, topic_id, format, results, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (learner_id, topic_id, format_type, json.dumps(results), now),
            )
        return self.get_diagnostics(learner_id)

    def get_diagnostics(self, learner_id, topic_id=None):
        with self._transaction() as conn:
            if topic_id:
                rows = conn.execute(
                    "SELECT * FROM diagnostics WHERE learner_id = ? AND topic_id = ? ORDER BY created_at DESC",
                    (learner_id, topic_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM diagnostics WHERE learner_id = ? ORDER BY created_at DESC",
                    (learner_id,),
                ).fetchall()
        return [dict(r) for r in rows]

    # ── Learning Paths ───────────────────────────────────────────────────
    def save_learning_path(self, learner_id, path_data):
        """path_data: JSON-serializable dict (e.g., from compute_learning_path)"""
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                "INSERT INTO learning_paths (learner_id, path_json, created_at) VALUES (?, ?, ?)",
                (learner_id, json.dumps(path_data), now),
            )
        return True

    def get_learning_paths(self, learner_id):
        with self._transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM learning_paths WHERE learner_id = ? ORDER BY created_at DESC",
                (learner_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ── System Logs ──────────────────────────────────────────────────────
    def log_event(self, event_type, data):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                "INSERT INTO system_logs (event_type, data, created_at) VALUES (?, ?, ?)",
                (event_type, json.dumps(data), now),
            )
        return True

    def get_logs(self, event_type=None, limit=100):
        with self._transaction() as conn:
            if event_type:
                rows = conn.execute(
                    "SELECT * FROM system_logs WHERE event_type = ? ORDER BY created_at DESC LIMIT ?",
                    (event_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM system_logs ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(r) for r in rows]

    # ── Users ────────────────────────────────────────────────────────────
    def create_user(self, user_id, email, password_hash, name=None, role="parent"):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO users (id, email, password_hash, name, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, email, password_hash, name, role, now, now),
            )
        return self.get_user(user_id)

    def get_user(self, user_id):
        with self._transaction() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return None
        user = dict(row)
        user.pop("password_hash", None)
        return user

    def get_user_by_email(self, email):
        with self._transaction() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            return None
        user = dict(row)
        user.pop("password_hash", None)
        return user

    def update_user_login(self, user_id):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (now, user_id),
            )

    def link_user_learner(self, user_id, learner_id):
        now = self._now()
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO user_learners (user_id, learner_id, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, learner_id) DO NOTHING
                """,
                (user_id, learner_id, now),
            )
        return True

    def get_user_learners(self, user_id):
        with self._transaction() as conn:
            rows = conn.execute(
                "SELECT learner_id FROM user_learners WHERE user_id = ?",
                (user_id,),
            ).fetchall()
        return [r["learner_id"] for r in rows]

    # ── Subscriptions ───────────────────────────────────────────────────
    def create_subscription(self, user_id, plan="free", stripe_subscription_id=None, 
                          stripe_customer_id=None, status="free", current_period_end=None):
        now = self._now()
        sub_id = f"sub_{self._now().replace(':', '-')}"
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions (id, user_id, stripe_subscription_id, stripe_customer_id, 
                    plan, status, current_period_end, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    stripe_subscription_id=excluded.stripe_subscription_id,
                    stripe_customer_id=excluded.stripe_customer_id,
                    plan=excluded.plan,
                    status=excluded.status,
                    current_period_end=excluded.current_period_end,
                    updated_at=excluded.updated_at
                """,
                (sub_id, user_id, stripe_subscription_id, stripe_customer_id, 
                 plan, status, current_period_end, now, now),
            )
        return self.get_subscription(user_id)

    def get_subscription(self, user_id):
        with self._transaction() as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            ).fetchone()
        if not row:
            return {"user_id": user_id, "plan": "free", "status": "free"}
        return dict(row)

    def update_subscription(self, user_id, **fields):
        allowed = {"plan", "status", "stripe_subscription_id", "stripe_customer_id", 
                   "current_period_end", "cancel_at_period_end"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_subscription(user_id)
        cols = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [self._now(), user_id]
        with self._transaction() as conn:
            conn.execute(
                f"UPDATE subscriptions SET {cols}, updated_at = ? WHERE user_id = ?",
                vals,
            )
        return self.get_subscription(user_id)

    # ── Profile Import / Export ──────────────────────────────────────────
    def import_json_profile(self, profile):
        """
        Import a legacy JSON profile into the database.
        profile: dict with keys matching the old JSON structure.
        """
        learner_id = profile.get("learnerId")
        meta = profile.get("metadata", {})

        # Create learner
        self.create_learner(
            learner_id=learner_id,
            name=meta.get("name"),
            age=meta.get("age"),
            grade=meta.get("grade"),
            notes=meta.get("notes", ""),
        )

        # Import mastery
        for tid, m in profile.get("masteryMap", {}).items():
            self.update_mastery(
                learner_id, tid,
                status=m.get("status", "not-started"),
                confidence=m.get("confidence"),
                notes=m.get("notes", ""),
            )

        # Import goals
        for g in profile.get("goals", []):
            self.add_goal(
                learner_id,
                target_topic_ids=g.get("targetTopicIds", []),
                deadline=g.get("deadline"),
                notes=g.get("notes", ""),
                status=g.get("status", "active"),
            )

        # Import diagnostics
        for d in profile.get("diagnostics", []):
            self.log_diagnostic(
                learner_id,
                d.get("topicId"),
                d.get("format", "unknown"),
                d.get("results", {}),
            )

        return self.export_profile(learner_id)

    def export_profile(self, learner_id):
        """Export a full learner profile in the legacy JSON format."""
        learner = self.get_learner(learner_id)
        if not learner:
            return None

        mastery = self.get_all_mastery(learner_id)
        goals = self.get_goals(learner_id)
        diagnostics = self.get_diagnostics(learner_id)
        paths = self.get_learning_paths(learner_id)

        return {
            "learnerId": learner_id,
            "createdAt": learner["created_at"],
            "updatedAt": learner["updated_at"],
            "metadata": {
                "name": learner["name"],
                "age": learner["age"],
                "grade": learner["grade"],
                "notes": learner["notes"],
            },
            "masteryMap": mastery,
            "goals": goals,
            "diagnostics": diagnostics,
            "learningPaths": paths,
        }

    # ── Stats ───────────────────────────────────────────────────────────
    def get_stats(self):
        with self._transaction() as conn:
            learners = conn.execute("SELECT COUNT(*) FROM learners").fetchone()[0]
            mastery = conn.execute("SELECT COUNT(*) FROM mastery").fetchone()[0]
            mastered = conn.execute(
                "SELECT COUNT(*) FROM mastery WHERE status = 'mastered'"
            ).fetchone()[0]
            goals = conn.execute("SELECT COUNT(*) FROM goals").fetchone()[0]
            diagnostics = conn.execute("SELECT COUNT(*) FROM diagnostics").fetchone()[0]
            logs = conn.execute("SELECT COUNT(*) FROM system_logs").fetchone()[0]

        return {
            "learners": learners,
            "masteryEntries": mastery,
            "masteredCount": mastered,
            "goals": goals,
            "diagnostics": diagnostics,
            "systemLogs": logs,
        }


# ---------------------------------------------------------------------------
# CLI / Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    db = MasteryGraphDB()
    print("=" * 60)
    print("MasteryGraph Core — SQLite Persistence Layer")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"\nSchema initialized. Tables:")
    print("  • learners")
    print("  • mastery")
    print("  • goals")
    print("  • diagnostics")
    print("  • learning_paths")
    print("  • system_logs")

    # Demo
    print(f"\n🧪 Demo:")
    learner_id = "db_demo_child"

    # Create
    db.create_learner(learner_id, name="Amara", age=7, grade="2nd", notes="Loves science")
    print(f"  Created learner: {db.get_learner(learner_id)['name']}")

    # Update mastery
    db.update_mastery(learner_id, "mt_yJmvUCCym7", "mastered", confidence=0.9, notes="Fluent")
    db.update_mastery(learner_id, "mt_IHipFGTFEY", "in-progress", confidence=0.5)
    print(f"  Mastery entries: {len(db.get_all_mastery(learner_id))}")
    print(f"  Mastered: {db.get_mastery_by_status(learner_id, 'mastered')}")

    # Goal
    db.add_goal(learner_id, ["mt_IHipFGTFEY"], notes="Master fractions by end of summer")
    print(f"  Goals: {len(db.get_goals(learner_id))}")

    # Diagnostic
    db.log_diagnostic(learner_id, "mt_IHipFGTFEY", "quiz", {"score": 0.6, "passed": False})
    print(f"  Diagnostics: {len(db.get_diagnostics(learner_id))}")

    # Log
    db.log_event("diagnostic_result", {"learnerId": learner_id, "topicId": "mt_IHipFGTFEY"})
    print(f"  System logs: {len(db.get_logs())}")

    # Export
    profile = db.export_profile(learner_id)
    print(f"\n  Exported profile keys: {list(profile.keys())}")
    print(f"  Mastery map size: {len(profile['masteryMap'])}")

    # Stats
    print(f"\n  Database stats: {db.get_stats()}")

    # Cleanup
    db.delete_learner(learner_id)
    print(f"\n  Deleted demo learner. Remaining: {db.get_stats()['learners']}")
    print(f"\n✅ SQLite persistence layer ready")
