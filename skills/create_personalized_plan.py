#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 7: create_personalized_plan
Combine path computation + gap analysis + learner profile + parent goals 
to output a weekly/daily learning plan.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add skills directory to path
sys.path.insert(0, str(Path(__file__).parent))
from compute_learning_path import LearningPathEngine
from analyze_gaps import GapAnalyzer
from update_learner_profile import LearnerProfileManager

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class PlanGenerator:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.path_engine = LearningPathEngine()
        self.gap_analyzer = GapAnalyzer()
        self.profile_mgr = LearnerProfileManager()
    
    def create_plan(self, learner_id, target_topic_ids=None, weeks=2, days_per_week=3, 
                    minutes_per_day=20, start_date=None):
        """
        Create a personalized learning plan.
        
        Args:
            learner_id: Learner ID
            target_topic_ids: List of target topics (or uses active goals)
            weeks: Number of weeks
            days_per_week: Sessions per week
            minutes_per_day: Target minutes per session
            start_date: Start date (default: today)
        
        Returns:
            Dict with weekly plan, daily breakdown, and rationale
        """
        # Load profile
        profile = self.profile_mgr.load_profile(learner_id)
        
        # Determine targets
        if not target_topic_ids:
            active_goals = [g for g in profile.get("goals", []) if g.get("status") == "active"]
            if active_goals:
                target_topic_ids = []
                for goal in active_goals:
                    target_topic_ids.extend(goal.get("targetTopicIds", []))
            else:
                return {"error": "No target topics specified and no active goals"}
        
        mastered = set(self.profile_mgr.get_all_mastered(learner_id))
        in_progress = set(self.profile_mgr.get_all_in_progress(learner_id))
        
        # Get gaps
        gap_analysis = self.gap_analyzer.analyze_gaps(
            target_topic_ids, 
            mastered_ids=list(mastered),
            in_progress_ids=list(in_progress)
        )
        
        # Get learning path
        path_result = self.path_engine.compute_path(
            target_topic_ids,
            mastered_ids=list(mastered)
        )
        
        # Build plan
        start_date = start_date or datetime.now()
        total_sessions = weeks * days_per_week
        
        # Distribute topics across sessions
        topics_to_cover = gap_analysis["gaps"][:total_sessions * 2]  # Up to 2 topics per session
        if not topics_to_cover:
            topics_to_cover = path_result["path"][:total_sessions]
        
        # Prioritize: critical gaps first, then path order
        prioritized = []
        critical_ids = {g["id"] for g in gap_analysis.get("criticalGaps", [])}
        
        # Add critical gaps first
        for g in gap_analysis["gaps"]:
            if g["id"] in critical_ids and g["id"] not in mastered and g["id"] not in in_progress:
                prioritized.append(g)
        
        # Add remaining path topics
        for step in path_result["path"]:
            if step["id"] not in {p["id"] for p in prioritized} and step["id"] not in mastered:
                # Find full gap info
                gap = next((g for g in gap_analysis["gaps"] if g["id"] == step["id"]), None)
                if gap:
                    prioritized.append(gap)
        
        # Build weekly schedule
        schedule = []
        topic_idx = 0
        
        for week in range(weeks):
            week_plan = {
                "week": week + 1,
                "startDate": (start_date + timedelta(weeks=week)).strftime("%Y-%m-%d"),
                "days": []
            }
            
            for day in range(days_per_week):
                if topic_idx >= len(prioritized):
                    break
                
                day_plan = {
                    "day": day + 1,
                    "date": (start_date + timedelta(weeks=week, days=day)).strftime("%Y-%m-%d"),
                    "durationMinutes": minutes_per_day,
                    "topics": [],
                    "activities": [],
                }
                
                # Assign 1-2 topics per session
                for _ in range(2):
                    if topic_idx >= len(prioritized):
                        break
                    
                    topic = prioritized[topic_idx]
                    topic_idx += 1
                    
                    day_plan["topics"].append({
                        "id": topic["id"],
                        "name": topic["name"],
                        "subject": topic["subject"],
                        "type": topic.get("type", "CONCEPTUAL"),
                        "centrality": topic.get("centrality", 0),
                        "assessmentPrompt": topic.get("assessmentPrompt", ""),
                    })
                
                # Suggest activities based on topic types
                day_plan["activities"] = self._suggest_day_activities(day_plan["topics"])
                
                week_plan["days"].append(day_plan)
            
            schedule.append(week_plan)
        
        return {
            "learnerId": learner_id,
            "planMeta": {
                "weeks": weeks,
                "daysPerWeek": days_per_week,
                "minutesPerDay": minutes_per_day,
                "totalSessions": total_sessions,
                "targetTopics": target_topic_ids,
            },
            "currentState": {
                "masteredCount": len(mastered),
                "inProgressCount": len(in_progress),
                "gapCount": gap_analysis["stats"]["totalGaps"],
                "criticalGapCount": gap_analysis["stats"]["criticalGaps"],
            },
            "schedule": schedule,
            "summary": f"{weeks}-week plan targeting {len(target_topic_ids)} topic(s). "
                      f"{gap_analysis['stats']['totalGaps']} gaps identified, "
                      f"{gap_analysis['stats']['criticalGaps']} critical. "
                      f"{len(mastered)} topics already mastered.",
        }
    
    def _suggest_day_activities(self, topics):
        """Suggest activities for a day's topics."""
        activities = []
        
        for topic in topics:
            ttype = topic.get("type", "CONCEPTUAL")
            subject = topic.get("subject", "").lower()
            
            if "math" in subject:
                if ttype == "PROCEDURAL":
                    activities.append(f"Practice {topic['name']} with 5 varied problems")
                else:
                    activities.append(f"Explore {topic['name']} using visual models or manipulatives")
            elif "english" in subject:
                activities.append(f"Read a short passage and identify {topic['name']}")
            elif "science" in subject:
                activities.append(f"Observe or experiment: {topic['name']}")
            else:
                activities.append(f"Discuss and practice: {topic['name']}")
        
        activities.append("Quick review of previously mastered topics")
        return activities

if __name__ == "__main__":
    gen = PlanGenerator()
    
    print("=" * 60)
    print("Skill 7: create_personalized_plan")
    print("=" * 60)
    
    # First, create a demo profile with some mastery
    learner_id = "demo_plan_child"
    mgr = LearnerProfileManager()
    mgr.create_profile(learner_id, name="Demo", age=7)
    
    # Mark some addition as mastered
    mgr.update_mastery(learner_id, "mt_yJmvUCCym7", "mastered", confidence=0.9)
    
    # Find a fractions topic
    fractions = [t for t in gen.topic_by_id.values() if "fractions" in t["name"].lower()]
    if fractions:
        target = fractions[0]
        print(f"\nTarget: {target['name']} ({target['id']})")
        
        plan = gen.create_plan(learner_id, target_topic_ids=[target["id"]], weeks=2, days_per_week=3)
        
        print(f"\n{plan['summary']}")
        print(f"\nCurrent state: {plan['currentState']}")
        
        for week in plan["schedule"]:
            print(f"\n📅 Week {week['week']} (starting {week['startDate']}):")
            for day in week["days"]:
                print(f"  Day {day['day']}: {day['durationMinutes']} min")
                for topic in day["topics"]:
                    print(f"    • {topic['name']} ({topic['subject']}, centrality: {topic['centrality']:.2f})")
