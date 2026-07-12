#!/usr/bin/env python3
"""Weekly digest cron — sends progress reports to all users with learners."""
import sys
import os
sys.path.insert(0, "/root/.openclaw/workspace")

import sqlite3
from datetime import datetime, timedelta
from masterygraph_core import MasteryGraphCore
from masterygraph_db import MasteryGraphDB
from email_service import email_service

def send_weekly_digests():
    db = MasteryGraphDB()
    core = MasteryGraphCore()
    
    # Connect to auth database for users
    import sqlite3
    auth_db = os.path.join(os.path.dirname(__file__), "masterygraph.db")
    conn = sqlite3.connect(auth_db)
    conn.row_factory = sqlite3.Row
    
    # Get all users with emails and their learners
    users = conn.execute("""
        SELECT u.id, u.email, u.name FROM users u
        WHERE u.email IS NOT NULL
    """).fetchall()
    
    sent = 0
    skipped = 0
    errors = 0
    
    for user in users:
        user_id = user["id"]
        email = user["email"]
        name = user["name"] or email
        
        # Get user's learners
        learners = conn.execute(
            "SELECT learner_id FROM user_learners WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        
        if not learners:
            skipped += 1
            continue
        
        for learner_row in learners:
            learner_id = learner_row[0]
            profile = core.get_profile(learner_id)
            if not profile:
                continue
            
            meta = profile.get("metadata", {})
            learner_name = meta.get("name", "Your learner")
            
            mastery = db.get_all_mastery(learner_id)
            mastered = sum(1 for m in mastery.values() if m.get("status") == "mastered")
            in_progress = sum(1 for m in mastery.values() if m.get("status") == "in-progress")
            
            # Compute gaps for any in-progress topic
            gaps = 0
            if in_progress > 0:
                for topic_id in [tid for tid, m in mastery.items() if m.get("status") == "in-progress"]:
                    try:
                        gap_result = core.analyze_gaps([topic_id], mastered_ids=[tid for tid, m in mastery.items() if m.get("status") == "mastered"])
                        gaps += len(gap_result.get("gaps", []))
                    except Exception:
                        pass
            
            week_start = (datetime.now() - timedelta(days=7)).strftime("%b %d")
            week_end = datetime.now().strftime("%b %d")
            
            stats = {
                "mastered": mastered,
                "in_progress": in_progress,
                "gaps": gaps,
                "week_start": f"{week_start} - {week_end}",
            }
            
            result = email_service.send_weekly_report(email, learner_name, stats)
            if result.get("status") == "sent":
                sent += 1
            elif result.get("status") == "skipped":
                skipped += 1
            else:
                errors += 1
                print(f"Error sending to {email}: {result}", file=sys.stderr)
    
    conn.close()
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "sent": sent,
        "skipped": skipped,
        "errors": errors,
    }
    print(f"Weekly digest complete: {summary}")
    return summary

if __name__ == "__main__":
    send_weekly_digests()
