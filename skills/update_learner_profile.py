#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 6: update_learner_profile
Persistently store/retrieve mastery status, confidence, goals, diagnostics,
and notes per micro-topic per child. Now backed by SQLite for speed and
reliability. JSON file export/import still supported for portability.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add workspace root so we can import masterygraph_db
sys.path.insert(0, str(Path(__file__).parent.parent))

from masterygraph_db import MasteryGraphDB

# Legacy JSON backup dir (kept for export/import compatibility)
PROFILE_DIR = Path("/root/.openclaw/workspace/masterygraph-profiles")
PROFILE_DIR.mkdir(exist_ok=True)

class LearnerProfileManager:
    """
    Manages learner profiles backed by SQLite.
    Mirrors the original JSON API so existing skills don't break.
    """
    def __init__(self, db=None):
        self.db = db or MasteryGraphDB()
    
    def _profile_path(self, learner_id):
        return PROFILE_DIR / f"{learner_id}.json"
    
    def _create_empty_profile(self, learner_id):
        return {
            "learnerId": learner_id,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "metadata": {
                "name": "",
                "age": None,
                "grade": None,
                "notes": "",
            },
            "masteryMap": {},
            "learningPaths": [],
            "diagnostics": [],
            "goals": [],
        }
    
    # ── Profile CRUD ────────────────────────────────────────────────────
    def create_profile(self, learner_id, name=None, age=None, grade=None, notes=""):
        """Create a new learner profile (SQLite-backed)."""
        self.db.create_learner(learner_id, name=name, age=age, grade=grade, notes=notes)
        return self.load_profile(learner_id)
    
    def load_profile(self, learner_id):
        """Load a learner's profile (DB-first, falls back to JSON)."""
        profile = self.db.export_profile(learner_id)
        if profile is not None:
            return profile
        
        # Fallback to JSON
        path = self._profile_path(learner_id)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._create_empty_profile(learner_id)
    
    def save_profile(self, profile):
        """Save a learner profile to DB and JSON backup."""
        # Always write to DB
        self.db.import_json_profile(profile)
        # Also write JSON backup for portability
        learner_id = profile.get("learnerId", "unknown")
        profile["updatedAt"] = datetime.now().isoformat()
        path = self._profile_path(learner_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)
        return profile
    
    # ── Mastery ─────────────────────────────────────────────────────────
    def update_mastery(self, learner_id, topic_id, status, confidence=None, notes=""):
        """Update mastery status for a specific topic."""
        # Ensure learner exists
        if not self.db.get_learner(learner_id):
            self.db.create_learner(learner_id)
        
        self.db.update_mastery(learner_id, topic_id, status, confidence, notes)
        return self.db.get_mastery(learner_id, topic_id)
    
    def bulk_update_mastery(self, learner_id, updates):
        """
        Bulk update mastery statuses.
        updates: List of dicts {topicId, status, confidence?, notes?}
        """
        if not self.db.get_learner(learner_id):
            self.db.create_learner(learner_id)
        
        self.db.bulk_update_mastery(learner_id, updates)
        return self.db.get_all_mastery(learner_id)
    
    def get_mastery_status(self, learner_id, topic_id):
        """Get mastery status for a specific topic."""
        return self.db.get_mastery(learner_id, topic_id)
    
    def get_all_mastered(self, learner_id):
        """Get all mastered topic IDs."""
        return self.db.get_mastery_by_status(learner_id, "mastered")
    
    def get_all_in_progress(self, learner_id):
        """Get all in-progress topic IDs."""
        return self.db.get_mastery_by_status(learner_id, "in-progress")
    
    # ── Goals ───────────────────────────────────────────────────────────
    def add_goal(self, learner_id, target_topic_ids, deadline=None, notes=""):
        """Add a learning goal."""
        if not self.db.get_learner(learner_id):
            self.db.create_learner(learner_id)
        
        self.db.add_goal(learner_id, target_topic_ids, deadline=deadline, notes=notes, status="active")
        return self.db.get_goals(learner_id)
    
    # ── Diagnostics ─────────────────────────────────────────────────────
    def log_diagnostic(self, learner_id, topic_id, format_type, results):
        """Log a diagnostic session."""
        if not self.db.get_learner(learner_id):
            self.db.create_learner(learner_id)
        
        self.db.log_diagnostic(learner_id, topic_id, format_type, results)
        return self.db.get_diagnostics(learner_id)
    
    # ── Export ──────────────────────────────────────────────────────────
    def export_profile(self, learner_id):
        """Export profile as JSON string."""
        profile = self.db.export_profile(learner_id)
        if profile is None:
            profile = self.load_profile(learner_id)
        return json.dumps(profile, indent=2)
    
    def list_learners(self):
        """List all learner IDs."""
        return [l["id"] for l in self.db.list_learners()]
    
    def delete_profile(self, learner_id):
        """Delete a learner profile."""
        self.db.delete_learner(learner_id)
        path = self._profile_path(learner_id)
        if path.exists():
            path.unlink()
        return True
    
    # ── Stats ───────────────────────────────────────────────────────────
    def get_stats(self):
        """Get database stats."""
        return self.db.get_stats()

if __name__ == "__main__":
    mgr = LearnerProfileManager()
    
    print("=" * 60)
    print("Skill 6: update_learner_profile (SQLite-backed)")
    print("=" * 60)
    
    # Demo
    learner_id = "demo_child_001"
    
    print(f"\nCreating profile for {learner_id}...")
    profile = mgr.create_profile(
        learner_id,
        name="Amara",
        age=7,
        grade="2nd",
        notes="Loves science, struggles with fractions"
    )
    print(f"Created: {profile['metadata']['name']}, age {profile['metadata']['age']}")
    
    # Update mastery
    print(f"\nUpdating mastery statuses...")
    mgr.update_mastery(learner_id, "mt_yJmvUCCym7", "mastered", confidence=0.9,
                      notes="Fluent with addition word problems")
    mgr.update_mastery(learner_id, "mt_IHipFGTFEY", "in-progress", confidence=0.5,
                      notes="Understands parts of a whole, needs work on equivalent fractions")
    
    # Check status
    status = mgr.get_mastery_status(learner_id, "mt_yJmvUCCym7")
    print(f"Addition word problems: {status['status']} (confidence: {status.get('confidence')})")
    
    # Get all mastered
    mastered = mgr.get_all_mastered(learner_id)
    print(f"Mastered topics: {len(mastered)}")
    
    # Add goal
    mgr.add_goal(learner_id, ["mt_IHipFGTFEY"], notes="Master fractions by end of summer")
    print(f"Goals: {len(mgr.db.get_goals(learner_id))}")
    
    # List learners
    learners = mgr.list_learners()
    print(f"\nAll learners: {learners}")
    
    # Stats
    print(f"\nDatabase stats: {mgr.get_stats()}")
    
    # Export
    print(f"\nProfile exported (JSON keys): {list(mgr.load_profile(learner_id).keys())}")
    
    # Cleanup
    mgr.delete_profile(learner_id)
    print(f"\nDeleted demo learner. Remaining: {mgr.get_stats()['learners']}")
    print(f"\n✅ SQLite-backed learner profile manager ready")
