#!/usr/bin/env python3
"""
OBIO Backend Test Suite
Run: pytest test_masterygraph_api.py -v
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

from masterygraph_api import app, get_key_mgr, get_auth_mgr, get_db, get_core

client = TestClient(app)

API_KEY = "mg-dev-local"
HEADERS = {"X-API-Key": API_KEY}

# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_test_data():
    """Clean up test data before each test."""
    db = get_db()
    # Remove test users and learners
    yield
    # Cleanup after test

# ── Health & Basic ─────────────────────────────────────────────────────

def test_health_endpoint():
    """Health check should return 200."""
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "db" in data

def test_api_key_required():
    """Endpoints should require API key."""
    response = client.get("/v1/learners")
    assert response.status_code == 403
    assert "X-API-Key" in response.json()["detail"]

def test_api_key_invalid():
    """Invalid API key should return 403."""
    response = client.get("/v1/learners", headers={"X-API-Key": "invalid"})
    assert response.status_code == 403

# ── Auth ───────────────────────────────────────────────────────────────

def test_register_and_login():
    """Full auth flow: register → login → access protected endpoint."""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass123!"
    
    # Register
    resp = client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email, "password": password, "name": "Test User", "role": "parent"
    })
    assert resp.status_code == 200, resp.text
    user = resp.json()["user"]
    assert user["email"] == email.lower()
    
    # Login
    resp = client.post("/v1/auth/login", headers=HEADERS, json={
        "email": email, "password": password
    })
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    assert token
    
    # Access protected endpoint
    resp = client.get("/v1/auth/me", headers={**HEADERS, "Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == email.lower()

def test_register_duplicate_email():
    """Registering same email twice should fail with clear error."""
    import uuid
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass123!"
    
    # First registration
    resp = client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email, "password": password, "name": "Test", "role": "parent"
    })
    assert resp.status_code == 200
    
    # Second registration
    resp = client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email, "password": password, "name": "Test2", "role": "parent"
    })
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()

def test_login_invalid_password():
    """Login with wrong password should fail."""
    import uuid
    email = f"badpass_{uuid.uuid4().hex[:8]}@example.com"
    
    # Register
    client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email, "password": "CorrectPass123!", "name": "Test", "role": "parent"
    })
    
    # Login with wrong password
    resp = client.post("/v1/auth/login", headers=HEADERS, json={
        "email": email, "password": "WrongPass123!"
    })
    assert resp.status_code == 401

# ── Learner Isolation (Critical Security) ────────────────────────────

def test_learner_isolation():
    """Users should only see their own learners."""
    import uuid
    
    # Create user A
    email_a = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email_a, "password": "SecurePass123!", "name": "User A", "role": "parent"
    })
    token_a = client.post("/v1/auth/login", headers=HEADERS, json={
        "email": email_a, "password": "SecurePass123!"
    }).json()["token"]
    
    # Create user B
    email_b = f"user_b_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email_b, "password": "SecurePass123!", "name": "User B", "role": "parent"
    })
    token_b = client.post("/v1/auth/login", headers=HEADERS, json={
        "email": email_b, "password": "SecurePass123!"
    }).json()["token"]
    
    # User A creates a learner
    resp = client.post("/v1/learners", headers={**HEADERS, "Authorization": f"Bearer {token_a}"}, json={
        "name": "Child A", "age": 8, "grade": "3rd"
    })
    assert resp.status_code == 200
    learner_a_id = resp.json()["id"]
    
    # User B creates a learner
    resp = client.post("/v1/learners", headers={**HEADERS, "Authorization": f"Bearer {token_b}"}, json={
        "name": "Child B", "age": 7, "grade": "2nd"
    })
    assert resp.status_code == 200
    learner_b_id = resp.json()["id"]
    
    # User A should only see Child A
    resp = client.get("/v1/learners", headers={**HEADERS, "Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 200
    learners = resp.json()["learners"]
    assert len(learners) == 1
    assert learners[0]["name"] == "Child A"
    
    # User B should only see Child B
    resp = client.get("/v1/learners", headers={**HEADERS, "Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 200
    learners = resp.json()["learners"]
    assert len(learners) == 1
    assert learners[0]["name"] == "Child B"
    
    # User A should NOT access User B's learner
    resp = client.get(f"/v1/learners/{learner_b_id}", headers={**HEADERS, "Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 403
    
    # User B should NOT access User A's learner
    resp = client.get(f"/v1/learners/{learner_a_id}", headers={**HEADERS, "Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 403

def test_learner_create_and_delete():
    """Create and delete a learner."""
    import uuid
    email = f"crud_{uuid.uuid4().hex[:8]}@example.com"
    
    # Register and login
    client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email, "password": "SecurePass123!", "name": "Test", "role": "parent"
    })
    token = client.post("/v1/auth/login", headers=HEADERS, json={
        "email": email, "password": "SecurePass123!"
    }).json()["token"]
    
    # Create learner
    resp = client.post("/v1/learners", headers={**HEADERS, "Authorization": f"Bearer {token}"}, json={
        "name": "Test Child", "age": 6, "grade": "1st"
    })
    assert resp.status_code == 200
    learner_id = resp.json()["id"]
    
    # Verify learner exists
    resp = client.get(f"/v1/learners/{learner_id}", headers={**HEADERS, "Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["metadata"]["name"] == "Test Child"
    
    # Delete learner
    resp = client.delete(f"/v1/learners/{learner_id}", headers={**HEADERS, "Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    
    # Verify deleted
    resp = client.get(f"/v1/learners/{learner_id}", headers={**HEADERS, "Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

# ── Topics & Search ──────────────────────────────────────────────────

def test_topic_search():
    """Topic search should return results."""
    resp = client.get("/v1/topics/search?q=addition", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0
    assert len(data["results"]) > 0

def test_topic_detail():
    """Topic detail should return topic info."""
    # First search for a topic
    resp = client.get("/v1/topics/search?q=addition", headers=HEADERS)
    topic_id = resp.json()["results"][0]["id"]
    
    # Get topic detail
    resp = client.get(f"/v1/topics/{topic_id}", headers=HEADERS)
    assert resp.status_code == 200
    assert "name" in resp.json()

# ── Learning Path ────────────────────────────────────────────────────

def test_learning_path():
    """Learning path should return ordered topics."""
    resp = client.get("/v1/topics/search?q=addition", headers=HEADERS)
    topic_id = resp.json()["results"][0]["id"]
    
    resp = client.post("/v1/path", headers=HEADERS, json={
        "target_topic_ids": [topic_id],
        "mastered_ids": [],
        "in_progress_ids": [],
        "max_steps": 5
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "path" in data
    assert "steps" in data

# ── Gap Analysis ─────────────────────────────────────────────────────

def test_gap_analysis():
    """Gap analysis should find prerequisites."""
    # Find a topic with known prerequisites (decimal place value)
    resp = client.get("/v1/topics/search?q=decimal%20place%20value", headers=HEADERS)
    if resp.json()["count"] == 0:
        pytest.skip("No decimal place value topics found")
    
    topic_id = resp.json()["results"][0]["id"]
    
    resp = client.post("/v1/gaps/analyze", headers=HEADERS, json={
        "target_topic_ids": [topic_id],
        "mastered_ids": [],
        "in_progress_ids": []
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "gaps" in data
    assert "stats" in data

# ── Assessment ───────────────────────────────────────────────────────

def test_assessment_public():
    """Assessment endpoint should work without auth."""
    resp = client.post("/v1/assessment", json={
        "child_age": 8,
        "topic_query": "addition"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "assessment" in data

# ── Pricing ──────────────────────────────────────────────────────────

def test_pricing():
    """Pricing endpoint should be public."""
    resp = client.get("/v1/pricing")
    assert resp.status_code == 200
    data = resp.json()
    assert "plans" in data
    assert len(data["plans"]) >= 2

# ── Audit Logging ────────────────────────────────────────────────────

def test_audit_log_created():
    """Audit logs should be created for auth events."""
    import uuid
    from audit_logger import get_audit_logger
    
    email = f"audit_{uuid.uuid4().hex[:8]}@example.com"
    
    # Register (should create audit log)
    client.post("/v1/auth/register", headers=HEADERS, json={
        "email": email, "password": "SecurePass123!", "name": "Audit Test", "role": "parent"
    })
    
    # Check audit logs
    audit = get_audit_logger()
    logs = audit.query(event_type="auth", limit=10)
    
    # Should have at least one auth log
    assert len(logs) > 0
    assert logs[0]["event_type"] == "auth"

# ── Security Headers ─────────────────────────────────────────────────

def test_cors_rejects_unauthorized_origin():
    """CORS should reject requests from unauthorized origins."""
    resp = client.get("/v1/health", headers={
        "Origin": "https://evil-site.com"
    })
    # CORS middleware allows the request but doesn't set Access-Control-Allow-Origin
    assert "access-control-allow-origin" not in resp.headers

def test_docs_disabled():
    """API docs should be disabled in production."""
    resp = client.get("/docs")
    assert resp.status_code == 404
    resp = client.get("/redoc")
    assert resp.status_code == 404
    resp = client.get("/openapi.json")
    assert resp.status_code == 404

# ── Rate Limiting ────────────────────────────────────────────────────

def test_rate_limit_headers():
    """Rate limit headers should be present on API key requests."""
    resp = client.get("/v1/health", headers=HEADERS)
    assert "x-ratelimit-limit" in resp.headers
    assert "x-ratelimit-remaining" in resp.headers

# ── Run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
