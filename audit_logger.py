#!/usr/bin/env python3
"""
Audit Logger — Security & Compliance Logging for OBIO
Logs all sensitive operations: auth, learner access, data mutations, payments
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

DB_PATH = Path("/root/.openclaw/workspace/masterygraph.db")

AUDIT_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    user_id     TEXT,
    ip_address  TEXT,
    resource    TEXT,
    action      TEXT,
    status      TEXT,
    details     TEXT,  -- JSON
    severity    TEXT DEFAULT 'info' CHECK(severity IN ('info', 'warning', 'critical'))
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
"""

class AuditLogger:
    """Security audit logging for sensitive operations."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(AUDIT_SCHEMA)
    
    def log(self, event_type: str, user_id: Optional[str] = None,
            ip_address: Optional[str] = None, resource: Optional[str] = None,
            action: Optional[str] = None, status: str = "success",
            details: Optional[Dict] = None, severity: str = "info"):
        """Log an audit event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO audit_log (timestamp, event_type, user_id, ip_address, 
                    resource, action, status, details, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datetime.now().isoformat(),
                    event_type,
                    user_id,
                    ip_address,
                    resource,
                    action,
                    status,
                    json.dumps(details) if details else None,
                    severity
                )
            )
    
    def log_auth(self, user_id: str, action: str, status: str = "success",
                 ip_address: Optional[str] = None, details: Optional[Dict] = None):
        """Log authentication events."""
        severity = "warning" if status == "failed" else "info"
        if action in ("password_reset", "forgot_password"):
            severity = "warning"
        self.log("auth", user_id, ip_address, "auth", action, status, details, severity)
    
    def log_learner_access(self, user_id: str, learner_id: str, action: str,
                           status: str = "success", ip_address: Optional[str] = None):
        """Log learner data access."""
        self.log("learner_access", user_id, ip_address, f"learner:{learner_id}", 
                 action, status, {"learner_id": learner_id})
    
    def log_data_mutation(self, user_id: str, resource: str, action: str,
                          status: str = "success", details: Optional[Dict] = None,
                          ip_address: Optional[str] = None):
        """Log data creation/update/deletion."""
        severity = "critical" if action == "delete" else "info"
        self.log("data_mutation", user_id, ip_address, resource, action, status, details, severity)
    
    def log_payment(self, user_id: str, action: str, status: str = "success",
                    details: Optional[Dict] = None, ip_address: Optional[str] = None):
        """Log payment events."""
        severity = "warning" if status == "failed" else "info"
        self.log("payment", user_id, ip_address, "payment", action, status, details, severity)
    
    def log_security(self, event_type: str, details: Dict, ip_address: Optional[str] = None,
                     severity: str = "warning"):
        """Log security events (rate limit, unauthorized access, etc.)."""
        self.log("security", None, ip_address, None, event_type, "triggered", details, severity)
    
    def query(self, user_id: Optional[str] = None, event_type: Optional[str] = None,
              start_time: Optional[str] = None, end_time: Optional[str] = None,
              limit: int = 100) -> list:
        """Query audit logs with filters."""
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

# Singleton instance
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
