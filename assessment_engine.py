"""Free Assessment Tool - Viral Acquisition Engine for OBIO.
Generates personalized prerequisite reports for any child + topic combo.
Requires no signup. Shareable URL. Upsell to paid plan."""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Assessment data storage
ASSESSMENTS_DIR = Path(os.getenv("ASSESSMENTS_DIR", "/root/.openclaw/workspace/assessments"))
ASSESSMENTS_DIR.mkdir(exist_ok=True)
ASSESSMENTS_FILE = ASSESSMENTS_DIR / "assessments.json"

class AssessmentEngine:
    """Generates free learning readiness assessments."""
    
    def __init__(self, taxonomy_path: str = None):
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.assessments = self._load_assessments()
    
    def _load_taxonomy(self, path: str = None) -> Dict:
        if path is None:
            path = "/root/.openclaw/workspace/marble-taxonomy/data/topics.json"
        try:
            with open(path) as f:
                data = json.load(f)
                return data.get("topics", [])
        except:
            return []
    
    def _load_assessments(self) -> Dict:
        if ASSESSMENTS_FILE.exists():
            with open(ASSESSMENTS_FILE) as f:
                return json.load(f)
        return {}
    
    def _save_assessments(self):
        with open(ASSESSMENTS_FILE, "w") as f:
            json.dump(self.assessments, f, indent=2)
    
    def find_topic(self, query: str) -> Optional[Dict]:
        """Find a topic by name or ID."""
        query = query.lower().strip()
        for topic in self.taxonomy:
            if query in topic.get("id", "").lower() or query in topic.get("name", "").lower():
                return topic
        return None
    
    def get_prerequisites(self, topic: Dict) -> List[Dict]:
        """Get prerequisite topics for a given topic."""
        prereq_ids = topic.get("prerequisites", [])
        prereqs = []
        for pid in prereq_ids:
            for t in self.taxonomy:
                if t.get("id") == pid:
                    prereqs.append(t)
                    break
        return prereqs
    
    def generate_assessment(self, child_age: int, topic_query: str, 
                           child_name: str = "", notes: str = "") -> Dict[str, Any]:
        """Generate a free assessment report."""
        topic = self.find_topic(topic_query)
        if not topic:
            # Try fuzzy matching
            topic = self._fuzzy_find_topic(topic_query)
        
        if not topic:
            return {
                "error": f"Topic '{topic_query}' not found. Try a different topic name.",
                "suggestions": self._get_suggestions(topic_query)
            }
        
        assessment_id = f"assmnt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
        
        # Get prerequisites
        prereqs = self.get_prerequisites(topic)
        
        # Filter by age appropriateness
        age_appropriate_prereqs = [
            p for p in prereqs 
            if p.get("ageRangeStart", 0) <= child_age + 2 and p.get("ageRangeEnd", 18) >= child_age - 2
        ]
        
        # Determine readiness
        readiness_level = self._calculate_readiness(child_age, topic, prereqs)
        
        # Generate assessment report
        report = {
            "assessment_id": assessment_id,
            "created_at": datetime.now().isoformat(),
            "child": {
                "name": child_name or "Your child",
                "age": child_age,
                "notes": notes,
            },
            "topic": {
                "id": topic.get("id"),
                "name": topic.get("name"),
                "description": topic.get("description", ""),
                "domain": topic.get("domain", ""),
                "subject": topic.get("subject", ""),
                "age_range": f"{topic.get('ageRangeStart', '?')}-{topic.get('ageRangeEnd', '?')}",
                "type": topic.get("type", ""),
            },
            "readiness": {
                "level": readiness_level,  # "ready", "almost_ready", "needs_prep", "too_advanced"
                "score": self._readiness_score(child_age, topic, prereqs),
                "explanation": self._readiness_explanation(readiness_level, child_age, topic, prereqs),
            },
            "prerequisites": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "description": p.get("description", "")[:100],
                    "age_range": f"{p.get('ageRangeStart', '?')}-{p.get('ageRangeEnd', '?')}",
                    "importance": "hard" if p.get("id") in topic.get("prerequisites", []) else "soft",
                }
                for p in prereqs[:10]  # Limit to 10 for readability
            ],
            "learning_path": self._generate_learning_path(topic, prereqs, child_age),
            "recommendations": self._generate_recommendations(readiness_level, child_age, topic, prereqs),
            "share_url": f"https://app.obiomacare.com/assessment/{assessment_id}",
            "upgrade_cta": {
                "text": "Get the full learning path with personalized plans, progress tracking, and AI tutoring",
                "url": f"https://app.obiomacare.com/register?assessment={assessment_id}",
            },
        }
        
        # Save assessment
        self.assessments[assessment_id] = report
        self._save_assessments()
        
        return report
    
    def _fuzzy_find_topic(self, query: str) -> Optional[Dict]:
        """Fuzzy match topic by keywords."""
        query_words = set(query.split())
        best_match = None
        best_score = 0
        
        for topic in self.taxonomy:
            name_words = set(topic.get("name", "").lower().split())
            desc_words = set(topic.get("description", "").lower().split())
            all_words = name_words | desc_words
            
            score = len(query_words & all_words)
            if score > best_score:
                best_score = score
                best_match = topic
        
        return best_match if best_score > 0 else None
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Get topic suggestions based on query."""
        query_lower = query.lower()
        suggestions = []
        for topic in self.taxonomy:
            if query_lower in topic.get("name", "").lower() or query_lower in topic.get("domain", "").lower():
                suggestions.append(topic.get("name"))
            if len(suggestions) >= 5:
                break
        return suggestions
    
    def _calculate_readiness(self, age: int, topic: Dict, prereqs: List[Dict]) -> str:
        """Calculate readiness level."""
        topic_min_age = topic.get("ageRangeStart", 5)
        topic_max_age = topic.get("ageRangeEnd", 18)
        
        if age < topic_min_age - 1:
            return "too_advanced"
        elif age > topic_max_age + 2:
            return "ready"  # Likely already knows it
        elif age >= topic_min_age:
            if len(prereqs) <= 2:
                return "ready"
            else:
                return "almost_ready"
        else:
            return "needs_prep"
    
    def _readiness_score(self, age: int, topic: Dict, prereqs: List[Dict]) -> int:
        """Calculate readiness score 0-100."""
        topic_min_age = topic.get("ageRangeStart", 5)
        topic_max_age = topic.get("ageRangeEnd", 18)
        
        if age > topic_max_age:
            return 100
        elif age >= topic_min_age:
            # Age-appropriate, score based on prerequisites
            base = 70
            if len(prereqs) > 5:
                base -= 10
            if len(prereqs) > 10:
                base -= 10
            return base
        else:
            # Below age range
            gap = topic_min_age - age
            return max(20, 50 - gap * 10)
    
    def _readiness_explanation(self, level: str, age: int, topic: Dict, prereqs: List[Dict]) -> str:
        """Generate human-readable readiness explanation."""
        explanations = {
            "ready": f"Your child is at the right age to start learning {topic.get('name')}! They have the cognitive foundation needed, and with {len(prereqs)} prerequisite topics to review, they're well-positioned to succeed.",
            "almost_ready": f"Your child is close to being ready for {topic.get('name')}. We recommend building comfort with the {len(prereqs)} prerequisite topics first. Most children master these in 2-4 weeks with consistent practice.",
            "needs_prep": f"{topic.get('name')} is a great goal, but your child will benefit from building foundational skills first. The {len(prereqs)} prerequisite topics create a strong learning ladder. Starting with the basics ensures confidence and prevents frustration.",
            "too_advanced": f"{topic.get('name')} is designed for slightly older children (ages {topic.get('ageRangeStart', '?')}-{topic.get('ageRangeEnd', '?')}). There are wonderful topics for a {age}-year-old that build toward this. Let's find the perfect starting point!",
        }
        return explanations.get(level, "Let's assess your child's readiness.")
    
    def _generate_learning_path(self, topic: Dict, prereqs: List[Dict], age: int) -> List[Dict]:
        """Generate a recommended learning path."""
        # Sort prerequisites by age appropriateness
        sorted_prereqs = sorted(prereqs, key=lambda p: p.get("ageRangeStart", 5))
        
        # Create learning path
        path = []
        for i, prereq in enumerate(sorted_prereqs[:5]):
            path.append({
                "step": i + 1,
                "topic_id": prereq.get("id"),
                "topic_name": prereq.get("name"),
                "estimated_time": "3-5 days" if prereq.get("type") == "CONCEPTUAL" else "5-7 days",
                "why": f"Builds the foundation for understanding {topic.get('name')}",
            })
        
        path.append({
            "step": len(path) + 1,
            "topic_id": topic.get("id"),
            "topic_name": topic.get("name"),
            "estimated_time": "1-2 weeks",
            "why": "The main goal!",
        })
        
        return path
    
    def _generate_recommendations(self, level: str, age: int, topic: Dict, prereqs: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        if level == "ready":
            recs.extend([
                "Start with the first prerequisite topic for 15 minutes daily",
                "Use real-world examples (cooking, shopping, games) to make concepts concrete",
                "Track progress weekly — celebrate small wins!",
            ])
        elif level == "almost_ready":
            recs.extend([
                "Spend 2-3 weeks on prerequisite topics before starting the main topic",
                "Use the 'prerequisite ladder' — don't skip steps, even if they seem easy",
                "Look for signs of mastery: can they explain the concept in their own words?",
            ])
        elif level == "needs_prep":
            recs.extend([
                "Start with age-appropriate topics in the same domain",
                "Focus on building number sense, spatial reasoning, or vocabulary (depending on subject)",
                "Games and play-based learning are more effective than worksheets at this stage",
            ])
        elif level == "too_advanced":
            recs.extend([
                f"Explore topics designed for ages {age-1}-{age+1} in the same subject",
                "Build foundational skills through stories, hands-on activities, and exploration",
                "Every child develops at their own pace — readiness is more important than age",
            ])
        
        return recs
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict]:
        """Retrieve a previously generated assessment."""
        return self.assessments.get(assessment_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get assessment statistics."""
        total = len(self.assessments)
        today = datetime.now().date()
        today_count = sum(1 for a in self.assessments.values() 
                         if datetime.fromisoformat(a["created_at"]).date() == today)
        
        # Count by readiness level
        readiness_counts = {}
        for a in self.assessments.values():
            level = a["readiness"]["level"]
            readiness_counts[level] = readiness_counts.get(level, 0) + 1
        
        return {
            "total_assessments": total,
            "today": today_count,
            "this_week": sum(1 for a in self.assessments.values() 
                            if (datetime.now() - datetime.fromisoformat(a["created_at"])).days <= 7),
            "readiness_distribution": readiness_counts,
            "top_topics": self._get_top_topics(),
        }
    
    def _get_top_topics(self) -> List[Dict]:
        """Get most assessed topics."""
        topic_counts = {}
        for a in self.assessments.values():
            tid = a["topic"]["id"]
            topic_counts[tid] = topic_counts.get(tid, {"count": 0, "name": a["topic"]["name"]})
            topic_counts[tid]["count"] += 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1]["count"], reverse=True)
        return [{"topic_id": tid, "name": info["name"], "count": info["count"]} 
                for tid, info in sorted_topics[:10]]

_engine = None

def get_assessment_engine() -> AssessmentEngine:
    global _engine
    if _engine is None:
        _engine = AssessmentEngine()
    return _engine
