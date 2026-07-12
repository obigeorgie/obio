#!/usr/bin/env python3
"""
MasteryGraph Core — FastAPI Wrapper (OBIO Edition)
Minimal REST API exposing all 12 skills programmatically.
All routes prefixed with /v1/ to match OBIO API spec.

Run:  python3 -m uvicorn masterygraph_api:app --reload --port 8000
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Header, Depends, Request, status, APIRouter, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))
from masterygraph_core import MasteryGraphCore
from masterygraph_db import MasteryGraphDB
from api_key_manager import APIKeyManager

from masterygraph_auth import AuthManager
from stripe_payments import get_stripe_manager, STRIPE_PRICE_FAMILY, STRIPE_PRICE_EDUCATOR
from email_service import email_service
from outreach_manager import get_outreach_manager

# ── Auth ─────────────────────────────────────────────────────────────────
_api_key_mgr = None
_auth_mgr = None

def get_key_mgr():
    global _api_key_mgr
    if _api_key_mgr is None:
        _api_key_mgr = APIKeyManager()
    return _api_key_mgr

def get_auth_mgr():
    global _auth_mgr
    if _auth_mgr is None:
        _auth_mgr = AuthManager()
    return _auth_mgr

# ── FastAPI App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="OBIO API",
    description="OBIO is the logic-driven, heart-aware learning engine that decodes exactly how your child learns best.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS for web frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Auth: exempt paths skip auth. Bearer tokens validate JWT. Otherwise require X-API-Key."""
    exempt_paths = ("/", "/health", "/docs", "/redoc", "/openapi.json",
                    "/v1/auth/register", "/v1/auth/login", "/v1/auth/forgot-password", "/v1/auth/reset-password",
                    "/v1/assessment", "/v1/analytics/track",
                    "/v1/content/stats", "/v1/content",
                    "/v1/pricing")
    if request.method == "OPTIONS" or request.url.path in exempt_paths:
        return await call_next(request)
    
    # Also exempt dynamic assessment paths and content
    if request.url.path.startswith("/v1/assessment/") or request.url.path.startswith("/v1/content/"):
        return await call_next(request)
    
    # Check Bearer token first (user auth)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        auth_mgr = get_auth_mgr()
        user = auth_mgr.verify_token(token)
        if user:
            # Valid JWT - attach user to request state for downstream use
            request.state.user = user
            return await call_next(request)
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )
    
    # Fall back to API key (machine-to-machine)
    api_key = request.headers.get("X-API-Key")
    mgr = get_key_mgr()
    if not api_key or not mgr.validate_key(api_key):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid or missing X-API-Key header"},
        )
    # Rate limit check
    allowed, remaining, reset = mgr.check_rate_limit(api_key)
    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded", "retry_after": reset},
        )
    response = await call_next(request)
    # Add rate limit headers
    info = mgr.validate_key(api_key)
    if info:
        response.headers["X-RateLimit-Limit"] = str(info["rate_limit"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response

# Shared instances (singleton pattern)
_core = None
_db = None

def get_core():
    global _core
    if _core is None:
        _core = MasteryGraphCore()
    return _core

def get_db():
    global _db
    if _db is None:
        _db = MasteryGraphDB()
    return _db

# ───────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ───────────────────────────────────────────────────────────────────────────

class LearnerCreate(BaseModel):
    learner_id: Optional[str] = Field(None, description="Unique learner identifier (auto-generated if not provided)")
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    notes: Optional[str] = ""

class MasteryUpdate(BaseModel):
    learner_id: str
    topic_id: str
    status: str = Field(..., pattern="^(mastered|in-progress|not-started)$")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: Optional[str] = ""

class MasteryUpdateById(BaseModel):
    topic_id: str
    status: str = Field(..., pattern="^(mastered|in-progress|not-started)$")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: Optional[str] = ""

class GapAnalysisAliasRequest(BaseModel):
    topic_id: str
    learner_id: Optional[str] = None

class PathComputeAliasRequest(BaseModel):
    target_topic_id: str
    learner_id: Optional[str] = None

class BulkMasteryUpdate(BaseModel):
    learner_id: str
    updates: List[Dict[str, Any]]

class GoalCreate(BaseModel):
    learner_id: str
    target_topic_ids: List[str]
    deadline: Optional[str] = None
    notes: Optional[str] = ""

class PathRequest(BaseModel):
    target_topic_ids: List[str]
    mastered_ids: Optional[List[str]] = []
    age: Optional[int] = None

class GapRequest(BaseModel):
    target_topic_ids: List[str]
    mastered_ids: Optional[List[str]] = []
    in_progress_ids: Optional[List[str]] = []

class DiagnosticRequest(BaseModel):
    topic_id: str
    format: str = "auto"
    age: Optional[int] = None

class ExplanationRequest(BaseModel):
    topic_id: str
    depth: int = 2
    age: Optional[int] = None

class PlanRequest(BaseModel):
    learner_id: str
    target_topic_ids: Optional[List[str]] = None
    weeks: int = 2
    days_per_week: int = 3
    minutes_per_day: int = 20

class ReportRequest(BaseModel):
    learner_id: str
    mastered_ids: List[str]
    in_progress_ids: Optional[List[str]] = []

class ContentRequest(BaseModel):
    topic_id: str
    content_type: str = Field(..., pattern="^(visual|video|storybook)$")
    format: Optional[str] = None
    age: Optional[int] = None
    duration: Optional[int] = None
    pages: Optional[int] = None

class StandardsRequest(BaseModel):
    topic_ids: List[str]

class DifficultyRequest(BaseModel):
    topic_id: str
    learner_age: Optional[int] = None

class LogEventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]

# Auth models
class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: Optional[str] = Field(None, description="Display name")
    role: Optional[str] = Field("parent", description="User role: parent, teacher, admin")

class LoginRequest(BaseModel):
    email: str
    password: str

class CheckoutRequest(BaseModel):
    plan: str = Field(..., pattern="^(family|educator)$")
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class CancelSubscriptionRequest(BaseModel):
    subscription_id: str

class SubscriptionStatusRequest(BaseModel):
    subscription_id: str

# ───────────────────────────────────────────────────────────────────────────
# v1 Router — All OBIO API routes under /v1/
# ───────────────────────────────────────────────────────────────────────────
v1 = APIRouter(prefix="/v1")

# ── Health & Meta ──────────────────────────────────────────────────────
@v1.get("/")
def v1_root():
    stripe_mgr = get_stripe_manager()
    return {
        "service": "OBIO API",
        "version": "1.0.0",
        "skills": 12,
        "topics": 1590,
        "dependencies": 3221,
        "payments_enabled": stripe_mgr.is_configured(),
    }

@v1.get("/health")
def v1_health():
    db = get_db()
    stats = db.get_stats()
    return {"status": "healthy", "db": stats, "timestamp": datetime.now().isoformat()}

# ── Taxonomy ───────────────────────────────────────────────────────────
@v1.get("/topics/search")
def v1_search_topics(q: str = Query(..., description="Search query")):
    core = get_core()
    results = core.search_topics(q)
    return {
        "query": q,
        "count": len(results),
        "results": [{"id": t["id"], "name": t["name"], "subject": t["subject"]} for t in results[:20]]
    }

@v1.get("/topics/{topic_id}")
def v1_get_topic(topic_id: str):
    core = get_core()
    topic = core.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

# ── Paths ────────────────────────────────────────────────────────────
@v1.post("/paths/compute")
def v1_compute_path(req: PathRequest):
    core = get_core()
    return core.compute_path(req.target_topic_ids, mastered_ids=req.mastered_ids or [], age=req.age)

# ── Gaps ─────────────────────────────────────────────────────────────
@v1.post("/gaps/analyze")
def v1_analyze_gaps(req: GapRequest):
    core = get_core()
    return core.analyze_gaps(req.target_topic_ids, mastered_ids=req.mastered_ids or [], in_progress_ids=req.in_progress_ids or [])

# ── Diagnostics ────────────────────────────────────────────────────
@v1.post("/diagnostics/generate")
def v1_generate_diagnostic(req: DiagnosticRequest):
    core = get_core()
    return core.generate_diagnostic(req.topic_id, req.format, req.age)

# ── Explain ──────────────────────────────────────────────────────────
@v1.post("/explain")
def v1_explain(req: ExplanationRequest):
    core = get_core()
    return core.explain(req.topic_id, req.depth, req.age)

# ── Learners ─────────────────────────────────────────────────────────
@v1.post("/learners")
def v1_create_learner(req: LearnerCreate):
    core = get_core()
    lid = req.learner_id or f"lrn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(req.name or '') % 10000:04d}"
    profile = core.create_profile(lid, name=req.name, age=req.age, grade=req.grade, notes=req.notes)
    if profile:
        profile["id"] = lid
    return profile

@v1.get("/learners")
def v1_list_learners():
    core = get_core()
    db = get_db()
    rows = db.list_learners()
    learners = []
    for row in rows:
        profile = core.get_profile(row["id"])
        mastery_count = len(profile.get("masteryMap", [])) if profile else 0
        learners.append({
            "id": row["id"],
            "name": row.get("name"),
            "age": row.get("age"),
            "grade": row.get("grade"),
            "mastery_count": mastery_count,
        })
    return {"learners": learners}

@v1.get("/learners/{learner_id}")
def v1_get_profile(learner_id: str):
    core = get_core()
    profile = core.get_profile(learner_id)
    if not profile or not profile.get("metadata"):
        raise HTTPException(status_code=404, detail="Learner not found")
    # Enrich with mastery list
    db = get_db()
    mastery_map = db.get_all_mastery(learner_id)
    profile["mastery"] = [
        {
            "topic_id": topic_id,
            "status": data.get("status"),
            "confidence": data.get("confidence"),
            "notes": data.get("notes"),
            "last_assessed": data.get("last_assessed"),
        }
        for topic_id, data in mastery_map.items()
    ]
    return profile

@v1.post("/learners/mastery")
def v1_update_mastery(req: MasteryUpdate):
    core = get_core()
    return core.update_mastery(req.learner_id, req.topic_id, req.status, req.confidence, req.notes)

@v1.post("/learners/{learner_id}/mastery")
def v1_update_mastery_by_id(learner_id: str, req: MasteryUpdateById):
    core = get_core()
    return core.update_mastery(learner_id, req.topic_id, req.status, req.confidence, req.notes)

@v1.get("/learners/{learner_id}/mastery")
def v1_get_mastery(learner_id: str):
    db = get_db()
    mastery_map = db.get_all_mastery(learner_id)
    mastery_list = []
    for topic_id, data in mastery_map.items():
        mastery_list.append({
            "topic_id": topic_id,
            "status": data.get("status"),
            "confidence": data.get("confidence"),
            "notes": data.get("notes"),
            "last_assessed": data.get("last_assessed"),
        })
    return {
        "learner_id": learner_id,
        "mastery": mastery_list
    }

@v1.post("/learners/mastery/bulk")
def v1_bulk_update_mastery(req: BulkMasteryUpdate):
    db = get_db()
    return db.bulk_update_mastery(req.learner_id, req.updates)

@v1.post("/learners/{learner_id}/mastery/bulk")
def v1_bulk_update_mastery_by_id(learner_id: str, req: BulkMasteryUpdate):
    db = get_db()
    return db.bulk_update_mastery(learner_id, req.updates)

@v1.get("/learners/{learner_id}/mastered")
def v1_get_mastered(learner_id: str):
    db = get_db()
    return {"learner_id": learner_id, "mastered": db.get_mastery_by_status(learner_id, "mastered")}

@v1.get("/learners/{learner_id}/in-progress")
def v1_get_in_progress(learner_id: str):
    db = get_db()
    return {"learner_id": learner_id, "in_progress": db.get_mastery_by_status(learner_id, "in-progress")}

@v1.delete("/learners/{learner_id}")
def v1_delete_learner(learner_id: str):
    core = get_core()
    core.delete_profile(learner_id)
    return {"deleted": True, "learner_id": learner_id}

# ── Plans ──────────────────────────────────────────────────────────────
@v1.post("/plans/create")
def v1_create_plan(req: PlanRequest):
    core = get_core()
    return core.create_plan(req.learner_id, target_topic_ids=req.target_topic_ids, weeks=req.weeks, days_per_week=req.days_per_week, minutes_per_day=req.minutes_per_day)

# ── Reports ──────────────────────────────────────────────────────────
@v1.post("/reports/cluster")
def v1_generate_cluster_report(req: ReportRequest):
    core = get_core()
    return core.generate_report(req.learner_id, req.mastered_ids, req.in_progress_ids or [])

# ── Standards ───────────────────────────────────────────────────────
@v1.post("/standards/align")
def v1_align_standards(req: StandardsRequest):
    core = get_core()
    return core.align_to_standards(req.topic_ids)

@v1.post("/standards/portfolio")
def v1_portfolio_report(req: ReportRequest):
    core = get_core()
    return core.portfolio_report(req.learner_id, req.mastered_ids, req.in_progress_ids or [])

# ── Difficulty ───────────────────────────────────────────────────────
@v1.post("/difficulty/estimate")
def v1_estimate_difficulty(req: DifficultyRequest):
    core = get_core()
    return core.estimate_difficulty(req.topic_id, req.learner_age)

# ── Content ──────────────────────────────────────────────────────────
@v1.post("/content/prepare")
def v1_prepare_content(req: ContentRequest):
    core = get_core()
    kwargs = {"age": req.age}
    if req.format: kwargs["format"] = req.format
    if req.duration: kwargs["duration"] = req.duration
    if req.pages: kwargs["pages"] = req.pages
    return core.prepare_content(req.topic_id, req.content_type, **kwargs)

# ── Logs ─────────────────────────────────────────────────────────────
@v1.post("/logs/event")
def v1_log_event(req: LogEventRequest):
    db = get_db()
    db.log_event(req.event_type, req.data)
    return {"logged": True, "event_type": req.event_type}

@v1.get("/logs")
def v1_get_logs(event_type: Optional[str] = None, limit: int = 100):
    db = get_db()
    return {"logs": db.get_logs(event_type, limit)}

# ── Analysis ─────────────────────────────────────────────────────────
@v1.get("/learners/{learner_id}/analyze")
def v1_analyze_learner(learner_id: str):
    core = get_core()
    return core.analyze_learner(learner_id)

@v1.get("/system/analysis")
def v1_system_analysis():
    core = get_core()
    return core.system_analysis()

@v1.get("/system/improvements")
def v1_suggest_improvements():
    core = get_core()
    return core.suggest_improvements()

# ── Alias endpoints for frontend compatibility ───────────────────────
@v1.post("/gap-analysis")
def v1_gap_analysis_alias(req: GapAnalysisAliasRequest):
    """Alias for /gaps/analyze that accepts {topic_id, learner_id} format."""
    core = get_core()
    db = get_db()
    
    # Get mastered and in-progress from learner profile
    mastered = []
    in_progress = []
    if req.learner_id:
        mastered = db.get_mastery_by_status(req.learner_id, "mastered")
        in_progress = db.get_mastery_by_status(req.learner_id, "in-progress")
    
    result = core.analyze_gaps([req.topic_id], mastered_ids=mastered, in_progress_ids=in_progress)
    result["target"] = {"id": req.topic_id, "name": req.topic_id}
    return result

@v1.post("/paths")
def v1_paths_alias(req: PathComputeAliasRequest):
    """Alias for /paths/compute that accepts {target_topic_id, learner_id} format."""
    core = get_core()
    db = get_db()
    
    mastered = []
    age = None
    if req.learner_id:
        mastered = db.get_mastery_by_status(req.learner_id, "mastered")
        profile = core.get_profile(req.learner_id)
        age = profile.get("metadata", {}).get("age") if profile else None
    
    return core.compute_path([req.target_topic_id], mastered_ids=mastered, age=age)

# ── Admin ────────────────────────────────────────────────────────────
@v1.get("/stats")
def v1_stats():
    db = get_db()
    return db.get_stats()

# ── Auth ─────────────────────────────────────────────────────────────
class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

@v1.post("/auth/forgot-password")
def v1_auth_forgot_password(req: PasswordResetRequest):
    """Request a password reset email. Always returns success (privacy)."""
    auth = get_auth_mgr()
    try:
        token = auth.generate_reset_token(req.email)
        # In production, send email with reset link
        # For now, return token directly for testing
        return {"success": True, "message": "If this email exists, a reset link has been sent.", "token": token}
    except ValueError:
        # Still return success to prevent email enumeration
        return {"success": True, "message": "If this email exists, a reset link has been sent."}

@v1.post("/auth/reset-password")
def v1_auth_reset_password(req: PasswordResetConfirm):
    """Reset password using a reset token."""
    auth = get_auth_mgr()
    if auth.reset_password(req.token, req.new_password):
        return {"success": True, "message": "Password reset successfully."}
    raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

@v1.post("/auth/update-password")
def v1_auth_update_password(req: UpdatePasswordRequest, authorization: str = Header(None)):
    """Update password with current password verification."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if auth.update_password(user["id"], req.current_password, req.new_password):
        return {"success": True, "message": "Password updated successfully."}
    raise HTTPException(status_code=400, detail="Current password is incorrect.")

@v1.post("/auth/update-profile")
def v1_auth_update_profile(req: UpdateProfileRequest, authorization: str = Header(None)):
    """Update user profile (name, email)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    auth.update_profile(user["id"], req.name, req.email)
    return {"success": True, "message": "Profile updated successfully."}

@v1.post("/auth/register")
def v1_auth_register(req: RegisterRequest):
    auth = get_auth_mgr()
    try:
        user = auth.register(req.email, req.password, req.name, req.role)
        return {"success": True, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@v1.post("/auth/login")
def v1_auth_login(req: LoginRequest):
    auth = get_auth_mgr()
    try:
        result = auth.login(req.email, req.password)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@v1.get("/auth/me")
def v1_auth_me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    # Get full user info + subscription
    full_user = auth.get_user(user["id"])
    db = get_db()
    sub = db.get_subscription(user["id"])
    full_user["subscription"] = {
        "plan": sub.get("plan", "free"),
        "status": sub.get("status", "free"),
    }
    return {"success": True, "user": full_user}

# ── Payments ─────────────────────────────────────────────────────────
@v1.post("/payments/create-checkout-session")
def v1_create_checkout(req: CheckoutRequest, authorization: str = Header(None)):
    """Create a Stripe checkout session for subscription."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    stripe_mgr = get_stripe_manager()
    if not stripe_mgr.is_configured():
        raise HTTPException(status_code=503, detail="Stripe payments not configured")
    
    try:
        session = stripe_mgr.create_checkout_session(
            user_email=user["email"],
            plan=req.plan,
            user_id=user["id"]
        )
        return {
            "success": True,
            "session_id": session["session_id"],
            "checkout_url": session["url"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@v1.post("/payments/cancel-subscription")
def v1_cancel_subscription(req: CancelSubscriptionRequest, authorization: str = Header(None)):
    """Cancel a subscription at period end."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    stripe_mgr = get_stripe_manager()
    if not stripe_mgr.is_configured():
        raise HTTPException(status_code=503, detail="Stripe payments not configured")
    
    try:
        result = stripe_mgr.cancel_subscription(req.subscription_id)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@v1.get("/payments/subscription-status")
def v1_subscription_status(subscription_id: str, authorization: str = Header(None)):
    """Get subscription status from Stripe."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    stripe_mgr = get_stripe_manager()
    if not stripe_mgr.is_configured():
        raise HTTPException(status_code=503, detail="Stripe payments not configured")
    
    return stripe_mgr.get_subscription_status(subscription_id)

@app.post("/v1/payments/webhook")
def v1_stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    stripe_mgr = get_stripe_manager()
    if not stripe_mgr.is_configured():
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    payload = request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    result = stripe_mgr.handle_webhook(payload, sig_header)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error", "Webhook error"))
    return result

# ── Email Notifications ────────────────────────────────────────────────
class SendWelcomeRequest(BaseModel):
    email: Optional[str] = None  # Uses user's email if not provided

@v1.post("/email/welcome")
def v1_send_welcome(req: SendWelcomeRequest, authorization: str = Header(None)):
    """Send welcome email to user or specified email."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = req.email or user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email available")
    
    result = email_service.send_welcome(email, user.get("name", ""))
    return {"success": result.get("status") in ("sent", "skipped"), "result": result}

class MasteryUpdateEmailRequest(BaseModel):
    learner_id: str
    topic_id: str
    status: str

@v1.post("/email/mastery-update")
def v1_send_mastery_update(req: MasteryUpdateEmailRequest, authorization: str = Header(None)):
    """Send mastery update notification email."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email available")
    
    core = get_core()
    profile = core.get_profile(req.learner_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Learner not found")
    
    topic = core.get_topic(req.topic_id)
    topic_name = topic.get("name", req.topic_id) if topic else req.topic_id
    learner_name = profile.get("metadata", {}).get("name", req.learner_id)
    
    result = email_service.send_mastery_update(email, learner_name, topic_name, req.status)
    return {"success": result.get("status") in ("sent", "skipped"), "result": result}

class WeeklyReportRequest(BaseModel):
    learner_id: str
    stats: Optional[Dict[str, Any]] = None

@v1.post("/email/weekly-report")
def v1_send_weekly_report(req: WeeklyReportRequest, authorization: str = Header(None)):
    """Send weekly progress report email."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email available")
    
    core = get_core()
    profile = core.get_profile(req.learner_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Learner not found")
    
    learner_name = profile.get("metadata", {}).get("name", req.learner_id)
    stats = req.stats or {}
    
    result = email_service.send_weekly_report(email, learner_name, stats)
    return {"success": result.get("status") in ("sent", "skipped"), "result": result}

from ai_tutor import get_tutor

# ── AI Tutor ──────────────────────────────────────────────────────────
class TutorExplainRequest(BaseModel):
    topic_id: str
    age: int = Field(..., ge=4, le=11)

class TutorPracticeRequest(BaseModel):
    topic_id: str
    age: int = Field(..., ge=4, le=11)
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    count: int = Field(3, ge=1, le=5)

class TutorQuestionRequest(BaseModel):
    question: str
    age: int = Field(..., ge=4, le=11)
    topic_id: Optional[str] = None

class TutorHintRequest(BaseModel):
    topic_id: str
    problem: str
    age: int = Field(..., ge=4, le=11)
    attempt_history: Optional[str] = ""

class TutorPathSummaryRequest(BaseModel):
    topic_ids: List[str]
    age: int = Field(..., ge=4, le=11)

class TutorAssessRequest(BaseModel):
    topic_id: str
    age: int = Field(..., ge=4, le=11)
    student_answer: str
    correct_answer: str

# ── AI Tutor ──────────────────────────────────────────────────────────
@v1.post("/tutor/explain")
def v1_tutor_explain(req: TutorExplainRequest, authorization: str = Header(None)):
    """Get an age-appropriate explanation of a topic."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    tutor = get_tutor()
    if not tutor.is_configured():
        raise HTTPException(status_code=503, detail="AI tutor not configured - set LLM_API_KEY")
    
    core = get_core()
    topic = core.get_topic(req.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get prerequisite names for context
    prereqs = []
    for dep_id in topic.get("dependencies", []):
        dep = core.get_topic(dep_id)
        if dep:
            prereqs.append(dep.get("name", dep_id))
    
    explanation = tutor.explain_topic(
        topic_name=topic.get("name", req.topic_id),
        topic_description=topic.get("description", ""),
        age=req.age,
        prerequisite_topics=prereqs[:5]  # Limit to first 5 for brevity
    )
    
    return {"success": True, "topic_id": req.topic_id, "explanation": explanation}

@v1.post("/tutor/practice")
def v1_tutor_practice(req: TutorPracticeRequest, authorization: str = Header(None)):
    """Generate practice problems for a topic."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    tutor = get_tutor()
    if not tutor.is_configured():
        raise HTTPException(status_code=503, detail="AI tutor not configured - set LLM_API_KEY")
    
    core = get_core()
    topic = core.get_topic(req.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    problems = tutor.generate_practice_problems(
        topic_name=topic.get("name", req.topic_id),
        age=req.age,
        difficulty=req.difficulty,
        count=req.count
    )
    
    return {"success": True, "topic_id": req.topic_id, "problems": problems}

@v1.post("/tutor/ask")
def v1_tutor_ask(req: TutorQuestionRequest, authorization: str = Header(None)):
    """Ask the AI tutor a question."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    tutor = get_tutor()
    if not tutor.is_configured():
        raise HTTPException(status_code=503, detail="AI tutor not configured - set LLM_API_KEY")
    
    topic_context = ""
    if req.topic_id:
        core = get_core()
        topic = core.get_topic(req.topic_id)
        if topic:
            topic_context = f"Topic: {topic.get('name', req.topic_id)}. {topic.get('description', '')}"
    
    answer = tutor.answer_question(req.question, req.age, topic_context)
    
    return {"success": True, "question": req.question, "answer": answer}

@v1.post("/tutor/hint")
def v1_tutor_hint(req: TutorHintRequest, authorization: str = Header(None)):
    """Get a hint for a problem without giving away the answer."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    tutor = get_tutor()
    if not tutor.is_configured():
        raise HTTPException(status_code=503, detail="AI tutor not configured - set LLM_API_KEY")
    
    core = get_core()
    topic = core.get_topic(req.topic_id)
    topic_name = topic.get("name", req.topic_id) if topic else req.topic_id
    
    hint = tutor.provide_hint(topic_name, req.problem, req.age, req.attempt_history)
    
    return {"success": True, "topic_id": req.topic_id, "hint": hint}

@v1.post("/tutor/path-summary")
def v1_tutor_path_summary(req: TutorPathSummaryRequest, authorization: str = Header(None)):
    """Generate a motivating summary of a learning path."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    tutor = get_tutor()
    if not tutor.is_configured():
        raise HTTPException(status_code=503, detail="AI tutor not configured - set LLM_API_KEY")
    
    core = get_core()
    topic_names = []
    for tid in req.topic_ids:
        topic = core.get_topic(tid)
        topic_names.append(topic.get("name", tid) if topic else tid)
    
    summary = tutor.generate_learning_path_summary(topic_names, req.age)
    
    return {"success": True, "summary": summary}

@v1.post("/tutor/assess")
def v1_tutor_assess(req: TutorAssessRequest, authorization: str = Header(None)):
    """Assess a student's understanding from their answer."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    tutor = get_tutor()
    if not tutor.is_configured():
        raise HTTPException(status_code=503, detail="AI tutor not configured - set LLM_API_KEY")
    
    core = get_core()
    topic = core.get_topic(req.topic_id)
    topic_name = topic.get("name", req.topic_id) if topic else req.topic_id
    
    assessment = tutor.assess_understanding(topic_name, req.age, req.student_answer, req.correct_answer)
    
    return {"success": True, "topic_id": req.topic_id, "assessment": assessment}

# ── Data Export ───────────────────────────────────────────────────────
class ExportRequest(BaseModel):
    format: str = Field("json", pattern="^(json|csv)$")
    learner_ids: Optional[List[str]] = None  # None = all learners for user

@v1.post("/export")
def v1_export_data(req: ExportRequest, authorization: str = Header(None)):
    """Export learner data (JSON or CSV format)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    auth = get_auth_mgr()
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    core = get_core()
    db = get_db()
    
    # Get all learners for this user
    all_learners = db.list_learners()
    learner_ids = req.learner_ids or [l["id"] for l in all_learners]
    
    data = []
    for lid in learner_ids:
        profile = core.get_profile(lid)
        if profile:
            mastery_map = db.get_all_mastery(lid)
            data.append({
                "learner_id": lid,
                "metadata": profile.get("metadata", {}),
                "mastery": [
                    {
                        "topic_id": tid,
                        "status": info.get("status"),
                        "confidence": info.get("confidence"),
                        "notes": info.get("notes"),
                        "last_assessed": info.get("last_assessed"),
                    }
                    for tid, info in mastery_map.items()
                ],
                "export_date": datetime.now().isoformat(),
            })
    
    if req.format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["learner_id", "name", "age", "grade", "topic_id", "status", "confidence", "last_assessed"])
        for entry in data:
            meta = entry["metadata"]
            for m in entry["mastery"]:
                writer.writerow([
                    entry["learner_id"],
                    meta.get("name", ""),
                    meta.get("age", ""),
                    meta.get("grade", ""),
                    m["topic_id"],
                    m["status"],
                    m["confidence"],
                    m["last_assessed"],
                ])
        return {"format": "csv", "data": output.getvalue()}
    
    return {"format": "json", "count": len(data), "learners": data}

from content_engine import get_content_engine, CONTENT_DIR

# ── Growth Engine ─────────────────────────────────────────────────────
from assessment_engine import get_assessment_engine
from analytics_tracker import get_tracker
from nurture_sequences import get_nurture

class CreateAssessmentRequest(BaseModel):
    child_age: int = Field(..., ge=4, le=18)
    topic_query: str
    child_name: str = ""
    parent_email: str = ""
    notes: str = ""

class TrackEventRequest(BaseModel):
    event_type: str
    properties: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ReferralRequest(BaseModel):
    referrer_id: str
    referred_email: str

# ── Free Assessment (Public, No Auth) ───────────────────────────────
@app.post("/v1/assessment")
def v1_create_assessment(req: CreateAssessmentRequest):
    """Create a free learning readiness assessment. No auth required."""
    engine = get_assessment_engine()
    result = engine.generate_assessment(
        child_age=req.child_age,
        topic_query=req.topic_query,
        child_name=req.child_name,
        notes=req.notes,
    )
    
    # Track the event
    tracker = get_tracker()
    tracker.track_event(
        event_type="assessment_complete",
        properties={
            "topic_id": result.get("topic", {}).get("id"),
            "topic_name": result.get("topic", {}).get("name"),
            "child_age": req.child_age,
            "readiness_level": result.get("readiness", {}).get("level"),
            "parent_email": req.parent_email,
        },
    )
    
    # If email provided, trigger nurture sequence
    if req.parent_email and "@" in req.parent_email:
        nurture = get_nurture()
        context = {
            "parent_name": req.parent_email.split("@")[0].replace(".", " ").title(),
            "child_name": req.child_name or "your child",
            "topic_name": result.get("topic", {}).get("name"),
            "readiness_level": result.get("readiness", {}).get("level"),
            "readiness_explanation": result.get("readiness", {}).get("explanation"),
            "prereq_count": len(result.get("prerequisites", [])),
            "assessment_id": result.get("assessment_id"),
            "learning_path": "\n".join([f"{p['step']}. {p['topic_name']} ({p['estimated_time']})" for p in result.get("learning_path", [])]),
        }
        email_result = nurture.send_sequence_email(
            user_email=req.parent_email,
            sequence_type="assessment",
            day=0,
            context=context,
        )
        result["email_sent"] = email_result.get("sent", False)
    
    return result

@app.get("/v1/assessment/{assessment_id}")
def v1_get_assessment(assessment_id: str):
    """Retrieve a previously generated assessment. No auth required."""
    engine = get_assessment_engine()
    result = engine.get_assessment(assessment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Track view
    tracker = get_tracker()
    tracker.track_event(
        event_type="assessment_viewed",
        properties={"assessment_id": assessment_id},
    )
    
    return result

@app.get("/v1/assessment/stats")
def v1_assessment_stats():
    """Get assessment statistics. Admin use."""
    engine = get_assessment_engine()
    return engine.get_stats()

# ── Analytics Tracking ────────────────────────────────────────────────
@app.post("/v1/analytics/track")
def v1_track_event(req: TrackEventRequest):
    """Track a user event. No auth required for anonymous tracking."""
    tracker = get_tracker()
    event = tracker.track_event(
        event_type=req.event_type,
        properties=req.properties,
        session_id=req.session_id,
    )
    return {"success": True, "event": event}

@app.get("/v1/analytics/funnel")
def v1_funnel_metrics(days: int = 30):
    """Get funnel metrics. Admin use."""
    tracker = get_tracker()
    return tracker.get_funnel_metrics(days)

@app.get("/v1/analytics/growth")
def v1_growth_metrics(days: int = 30):
    """Get growth metrics. Admin use."""
    tracker = get_tracker()
    return tracker.get_growth_metrics(days)

@app.get("/v1/analytics/dashboard")
def v1_analytics_dashboard():
    """Get complete analytics dashboard. Admin use."""
    tracker = get_tracker()
    return tracker.get_dashboard_summary()

# ── Referral System ───────────────────────────────────────────────────
@app.post("/v1/referral")
def v1_create_referral(req: ReferralRequest):
    """Create a referral link."""
    tracker = get_tracker()
    
    # Track referral
    tracker.track_event(
        event_type="referral_shared",
        user_id=req.referrer_id,
        properties={"referred_email": req.referred_email},
    )
    
    referral_code = f"ref_{req.referrer_id}_{os.urandom(4).hex()}"
    
    return {
        "success": True,
        "referral_code": referral_code,
        "share_url": f"https://app.obiomacare.com/register?ref={referral_code}",
        "referrer_id": req.referrer_id,
    }

@app.post("/v1/referral/convert")
def v1_convert_referral(referral_code: str, new_user_id: str):
    """Mark a referral as converted when new user signs up."""
    tracker = get_tracker()
    tracker.track_event(
        event_type="referral_converted",
        user_id=new_user_id,
        properties={"referral_code": referral_code},
    )
    return {"success": True, "referral_code": referral_code, "new_user_id": new_user_id}

# ── Nurture Sequences ─────────────────────────────────────────────────
@app.post("/v1/nurture/send")
def v1_send_nurture_email(user_email: str, sequence_type: str, day: int, 
                          context: Dict[str, Any] = Body(...)):
    """Send a nurture sequence email. Admin use."""
    nurture = get_nurture()
    result = nurture.send_sequence_email(user_email, sequence_type, day, context)
    return result

@app.post("/v1/nurture/next")
def v1_get_next_nurture_emails(user_email: str, sequence_type: str, 
                               start_date: str, current_status: Dict[str, Any] = Body(...)):
    """Get next emails in a nurture sequence. Admin use."""
    nurture = get_nurture()
    from datetime import datetime
    start = datetime.fromisoformat(start_date)
    emails = nurture.get_next_emails(user_email, sequence_type, start, current_status)
    return {"next_emails": emails}

# ── Content Engine ────────────────────────────────────────────────────
@app.post("/v1/content/generate")
def v1_generate_content(topic_id: Optional[str] = None, count: int = 1, subject: Optional[str] = None):
    """Generate SEO blog posts from taxonomy. Admin use."""
    engine = get_content_engine()
    
    if topic_id:
        post = engine.generate_blog_post(topic_id)
        return {"success": True, "posts": [post] if post else []}
    else:
        posts = engine.generate_batch(count=count, subject_filter=subject)
        return {"success": True, "posts": posts, "count": len(posts)}

@app.get("/v1/content/stats")
def v1_content_stats():
    """Get content generation stats. Admin use."""
    engine = get_content_engine()
    return engine.get_content_stats()

@app.get("/v1/content/{slug}")
def v1_get_content(slug: str):
    """Get a generated blog post. Public."""
    filepath = CONTENT_DIR / f"{slug}.md"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Content not found")
    
    with open(filepath) as f:
        content = f.read()
    
    return {"slug": slug, "content": content}

from outreach_manager import get_outreach_manager

# ── Outreach API ──────────────────────────────────────────────────────
@app.post("/v1/outreach/contact")
def v1_add_outreach_contact(contact_type: str, name: str, email: str,
                             organization: str = "", notes: str = "",
                             platform: str = "", website: str = ""):
    """Add a new outreach contact. Admin use."""
    manager = get_outreach_manager()
    contact = manager.add_contact(contact_type, name, email, organization, notes, platform, website)
    return {"success": True, "contact": contact}

@app.post("/v1/outreach/generate-email/{contact_id}")
def v1_generate_outreach_email(contact_id: str, template_name: Optional[str] = None):
    """Generate outreach email for a contact. Admin use."""
    manager = get_outreach_manager()
    email = manager.generate_outreach_email(contact_id, template_name)
    if not email:
        raise HTTPException(status_code=404, detail="Contact or template not found")
    return {"success": True, "email": email}

@app.get("/v1/outreach/stats")
def v1_outreach_stats():
    """Get outreach statistics. Admin use."""
    manager = get_outreach_manager()
    return manager.get_stats()

@app.get("/v1/outreach/export")
def v1_export_outreach():
    """Export contacts as CSV. Admin use."""
    manager = get_outreach_manager()
    csv_data = manager.export_csv()
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=csv_data, media_type="text/csv")

# ── Public Pricing (No Auth) ─────────────────────────────────────────
@app.get("/v1/pricing")
def v1_get_pricing():
    """Get pricing plans. Public endpoint."""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "interval": "month",
                "features": [
                    "Unlimited assessments",
                    "1 learner",
                    "5 AI tutor sessions/day",
                    "Basic progress tracking",
                ],
                "cta": "Get Started",
                "url": "/assessment",
            },
            {
                "id": "family",
                "name": "Family",
                "price": 12,
                "interval": "month",
                "price_id": STRIPE_PRICE_FAMILY,
                "features": [
                    "Unlimited learners",
                    "Unlimited AI tutor",
                    "Weekly email reports",
                    "Full mastery analytics",
                    "Learning path generation",
                ],
                "cta": "Start Free Trial",
                "popular": True,
            },
            {
                "id": "educator",
                "name": "Educator",
                "price": 29,
                "interval": "month",
                "price_id": STRIPE_PRICE_EDUCATOR,
                "features": [
                    "Everything in Family",
                    "Up to 20 learners",
                    "Bulk import/export",
                    "Priority support",
                ],
                "cta": "Get Started",
            },
        ],
        "currency": "usd",
    }

# ── Include the v1 router ────────────────────────────────────────────
app.include_router(v1)

# ── Legacy root routes (no auth required) ────────────────────────────
@app.get("/")
def root():
    return {
        "service": "OBIO API",
        "version": "1.0.0",
        "message": "OBIO is the logic-driven, heart-aware learning engine that decodes exactly how your child learns best.",
        "docs": "/docs",
        "api_base": "/v1",
    }

@app.get("/health")
def health():
    db = get_db()
    stats = db.get_stats()
    return {"status": "healthy", "db": stats, "timestamp": datetime.now().isoformat()}

# ───────────────────────────────────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
