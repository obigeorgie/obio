"""Analytics and Tracking module for MasteryGraph.
Captures user events, funnel metrics, and growth KPIs."""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Analytics data directory
ANALYTICS_DIR = Path(os.getenv("ANALYTICS_DIR", "/root/.openclaw/workspace/analytics"))
ANALYTICS_DIR.mkdir(exist_ok=True)

EVENTS_FILE = ANALYTICS_DIR / "events.jsonl"
FUNNEL_FILE = ANALYTICS_DIR / "funnel.json"
METRICS_FILE = ANALYTICS_DIR / "metrics.json"

class AnalyticsTracker:
    """Tracks user events, funnel stages, and growth metrics."""
    
    FUNNEL_STAGES = [
        "landing_visit",
        "assessment_start",
        "assessment_complete",
        "signup_initiated",
        "signup_completed",
        "onboarding_started",
        "onboarding_completed",
        "learner_added",
        "topic_searched",
        "path_viewed",
        "gap_analysis_viewed",
        "upgrade_viewed",
        "checkout_initiated",
        "checkout_completed",
        "subscription_active",
        "referral_shared",
        "referral_converted",
        "weekly_email_open",
        "weekly_email_click",
        "content_shared",
        "partner_referred",
    ]
    
    def __init__(self):
        self.events_file = EVENTS_FILE
        self.funnel_file = FUNNEL_FILE
        self.metrics_file = METRICS_FILE
    
    def track_event(self, event_type: str, user_id: Optional[str] = None, 
                    properties: Optional[Dict[str, Any]] = None, 
                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """Track a single user event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "session_id": session_id,
            "properties": properties or {},
        }
        
        # Append to events file
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        # Update funnel if applicable
        if event_type in self.FUNNEL_STAGES:
            self._update_funnel(user_id, event_type, event["timestamp"])
        
        return event
    
    def _update_funnel(self, user_id: Optional[str], stage: str, timestamp: str):
        """Update user's position in the funnel."""
        if not user_id:
            return
        
        funnel_data = self._load_funnel()
        if user_id not in funnel_data:
            funnel_data[user_id] = {}
        
        funnel_data[user_id][stage] = timestamp
        self._save_funnel(funnel_data)
    
    def _load_funnel(self) -> Dict:
        if self.funnel_file.exists():
            with open(self.funnel_file) as f:
                return json.load(f)
        return {}
    
    def _save_funnel(self, data: Dict):
        with open(self.funnel_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_funnel_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get funnel conversion metrics for the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        funnel_data = self._load_funnel()
        
        metrics = {}
        for stage in self.FUNNEL_STAGES:
            count = sum(1 for user_stages in funnel_data.values() 
                       if stage in user_stages and datetime.fromisoformat(user_stages[stage]) > cutoff)
            metrics[stage] = count
        
        # Calculate conversion rates
        conversions = {}
        for i, stage in enumerate(self.FUNNEL_STAGES[1:], 1):
            prev_stage = self.FUNNEL_STAGES[i-1]
            if metrics[prev_stage] > 0:
                conversions[f"{prev_stage}_to_{stage}"] = round(metrics[stage] / metrics[prev_stage] * 100, 1)
            else:
                conversions[f"{prev_stage}_to_{stage}"] = 0.0
        
        return {
            "period_days": days,
            "stage_counts": metrics,
            "conversion_rates": conversions,
            "total_users": len(funnel_data),
        }
    
    def get_growth_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get key growth metrics."""
        events = self._load_events(days)
        
        # Count unique events
        event_counts = {}
        for event in events:
            et = event["event_type"]
            event_counts[et] = event_counts.get(et, 0) + 1
        
        # Unique users
        unique_users = set(e["user_id"] for e in events if e["user_id"])
        
        # Referral tracking
        referrals = [e for e in events if e["event_type"] == "referral_converted"]
        
        # Revenue estimate (from checkout_completed events)
        revenue_events = [e for e in events if e["event_type"] == "checkout_completed"]
        estimated_revenue = sum(
            e["properties"].get("amount", 0) for e in revenue_events
        )
        
        return {
            "period_days": days,
            "total_events": len(events),
            "unique_users": len(unique_users),
            "event_counts": event_counts,
            "referrals": len(referrals),
            "estimated_revenue_cents": estimated_revenue,
            "estimated_revenue_usd": round(estimated_revenue / 100, 2),
        }
    
    def _load_events(self, days: int = 30) -> List[Dict]:
        """Load events from the last N days."""
        if not self.events_file.exists():
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        events = []
        
        with open(self.events_file) as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if event_time > cutoff:
                        events.append(event)
                except (json.JSONDecodeError, ValueError):
                    continue
        
        return events
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get complete dashboard summary."""
        today = datetime.now().date()
        
        # Today's events
        today_events = self._load_events(1)
        
        # This week's events
        week_events = self._load_events(7)
        
        # This month's events
        month_events = self._load_events(30)
        
        funnel = self.get_funnel_metrics(30)
        growth = self.get_growth_metrics(30)
        
        # Calculate CAC (estimated)
        paid_users = funnel["stage_counts"].get("checkout_completed", 0)
        # Rough estimate: assume $0.50 per visitor in ad spend
        visitors = funnel["stage_counts"].get("landing_visit", 0)
        estimated_cac = round(0.50 * visitors / max(paid_users, 1), 2)
        
        # LTV estimate (assume 8 months average retention)
        avg_monthly = 12  # Family plan
        estimated_ltv = round(avg_monthly * 8, 2)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "today": {
                "events": len(today_events),
                "unique_users": len(set(e["user_id"] for e in today_events if e["user_id"])),
                "new_signups": sum(1 for e in today_events if e["event_type"] == "signup_completed"),
                "checkouts": sum(1 for e in today_events if e["event_type"] == "checkout_completed"),
            },
            "this_week": {
                "events": len(week_events),
                "unique_users": len(set(e["user_id"] for e in week_events if e["user_id"])),
                "new_signups": sum(1 for e in week_events if e["event_type"] == "signup_completed"),
                "checkouts": sum(1 for e in week_events if e["event_type"] == "checkout_completed"),
            },
            "this_month": {
                "events": len(month_events),
                "unique_users": len(set(e["user_id"] for e in month_events if e["user_id"])),
                "new_signups": sum(1 for e in month_events if e["event_type"] == "signup_completed"),
                "checkouts": sum(1 for e in month_events if e["event_type"] == "checkout_completed"),
            },
            "funnel": funnel,
            "growth": growth,
            "estimated_cac": estimated_cac,
            "estimated_ltv": estimated_ltv,
            "ltv_cac_ratio": round(estimated_ltv / max(estimated_cac, 0.01), 2),
            "mrr_estimate": round(paid_users * avg_monthly, 2),
        }

_tracker = None

def get_tracker() -> AnalyticsTracker:
    global _tracker
    if _tracker is None:
        _tracker = AnalyticsTracker()
    return _tracker
