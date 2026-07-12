#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 5: generate_grounded_explanation
Explain a micro-topic or concept while explicitly referencing its direct 
prerequisites and why they matter. Never skip foundations.
"""

import json
from pathlib import Path

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class ExplanationEngine:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.prereqs_for = load_index("dependencies_by_topic")
    
    def explain(self, topic_id, depth=2, age=None, include_activities=True):
        """
        Generate a grounded explanation for a topic.
        
        Args:
            topic_id: The topic to explain
            depth: How many levels of prerequisites to surface
            age: Target age for tone/complexity
            include_activities: Whether to suggest practice activities
        
        Returns:
            Dict with structured explanation, prerequisites, and activities
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        age = age or topic.get("ageRangeStart", 6)
        
        # Get direct prerequisites
        direct_prereqs = self.prereqs_for.get(topic_id, [])
        prereq_details = []
        
        for d in direct_prereqs:
            pid = d["prerequisiteId"]
            ptopic = self.topic_by_id.get(pid)
            if ptopic:
                prereq_details.append({
                    "id": pid,
                    "name": ptopic.get("name"),
                    "subject": ptopic.get("subject"),
                    "strength": d.get("strength", "hard"),
                    "reason": d.get("reason", ""),
                    "description": ptopic.get("description", "")[:200],
                })
        
        # Sort: hard first
        prereq_details.sort(key=lambda p: 0 if p["strength"] == "hard" else 1)
        
        # Get indirect prerequisites (if depth > 1)
        indirect = []
        if depth > 1:
            seen = {p["id"] for p in prereq_details}
            for p in prereq_details:
                sub_prereqs = self.prereqs_for.get(p["id"], [])
                for sp in sub_prereqs:
                    spid = sp["prerequisiteId"]
                    if spid not in seen and spid != topic_id:
                        seen.add(spid)
                        sptopic = self.topic_by_id.get(spid)
                        if sptopic:
                            indirect.append({
                                "id": spid,
                                "name": sptopic.get("name"),
                                "subject": sptopic.get("subject"),
                                "strength": sp.get("strength", "hard"),
                                "reason": sp.get("reason", ""),
                            })
        
        # Build explanation
        explanation = {
            "topic": {
                "id": topic_id,
                "name": topic.get("name"),
                "subject": topic.get("subject"),
                "domain": topic.get("domain"),
                "description": topic.get("description", ""),
                "ageRange": f"{topic.get('ageRangeStart')}-{topic.get('ageRangeEnd')}",
            },
            "directPrerequisites": prereq_details,
            "indirectPrerequisites": indirect[:5] if indirect else [],  # Cap at 5
            "whyThisMatters": self._generate_why_matters(topic, prereq_details),
            "howToLearn": self._generate_learning_steps(topic, prereq_details, age),
        }
        
        if include_activities:
            explanation["suggestedActivities"] = self._suggest_activities(topic, age)
        
        return explanation
    
    def _generate_why_matters(self, topic, prereqs):
        """Generate why this topic matters text."""
        name = topic.get("name", "this topic")
        subject = topic.get("subject", "learning")
        
        reasons = [f"{name} is a fundamental building block in {subject}."]
        
        if prereqs:
            hard_count = sum(1 for p in prereqs if p["strength"] == "hard")
            if hard_count > 0:
                reasons.append(f"It builds directly on {hard_count} essential prerequisite(s), "
                             f"making it a critical junction point in the learning graph.")
            
            # Mention what it unlocks
            reasons.append("Mastering this opens the door to more advanced concepts that depend on it.")
        
        return reasons
    
    def _generate_learning_steps(self, topic, prereqs, age):
        """Generate step-by-step learning approach."""
        steps = []
        
        # Step 1: Review prerequisites
        hard_prereqs = [p for p in prereqs if p["strength"] == "hard"]
        if hard_prereqs:
            steps.append({
                "step": 1,
                "action": "Review prerequisites",
                "details": f"Make sure you're comfortable with: {', '.join(p['name'] for p in hard_prereqs[:3])}",
                "why": "These foundations are essential — skipping them leads to confusion later.",
            })
        
        # Step 2: Core concept
        steps.append({
            "step": len(steps) + 1,
            "action": "Understand the core concept",
            "details": topic.get("description", f"Learn what {topic['name']} means and why it works.")[:300],
            "why": "Conceptual understanding comes before procedural fluency.",
        })
        
        # Step 3: Practice
        steps.append({
            "step": len(steps) + 1,
            "action": "Practice with varied examples",
            "details": "Work through problems in different contexts to build flexibility.",
            "why": "Mastery requires seeing the concept in multiple situations.",
        })
        
        # Step 4: Apply
        steps.append({
            "step": len(steps) + 1,
            "action": "Apply to new situations",
            "details": "Try using this skill to solve problems you haven't seen before.",
            "why": "True mastery means you can use this skill when you need it, not just when prompted.",
        })
        
        return steps
    
    def _suggest_activities(self, topic, age):
        """Suggest age-appropriate activities."""
        activities = []
        subject = topic.get("subject", "").lower()
        
        if "math" in subject:
            activities = [
                "Use physical objects (blocks, coins) to model the concept",
                "Create a real-world story problem using this skill",
                "Teach the concept to a stuffed animal or family member",
            ]
        elif "english" in subject or "reading" in subject:
            activities = [
                "Find examples in a favorite book",
                "Write a short story using this technique",
                "Play a word game that reinforces the pattern",
            ]
        elif "science" in subject:
            activities = [
                "Do a simple experiment at home",
                "Observe the concept in nature or daily life",
                "Draw a diagram explaining how it works",
            ]
        else:
            activities = [
                "Discuss how you use this in daily life",
                "Create a visual poster or chart",
                "Practice with a partner or family member",
            ]
        
        return activities[:3]

if __name__ == "__main__":
    engine = ExplanationEngine()
    
    print("=" * 60)
    print("Skill 5: generate_grounded_explanation")
    print("=" * 60)
    
    # Demo: Explain fractions
    results = [t for t in engine.topic_by_id.values() if "fractions" in t["name"].lower()]
    if results:
        target = results[0]
        print(f"\nTopic: {target['name']} ({target['id']})")
        
        expl = engine.explain(target["id"], age=7)
        
        print(f"\n📚 Description: {expl['topic']['description'][:150]}...")
        
        print(f"\n🔗 Direct Prerequisites ({len(expl['directPrerequisites'])}):")
        for p in expl["directPrerequisites"][:5]:
            strength_emoji = "🔴" if p["strength"] == "hard" else "🟡"
            print(f"  {strength_emoji} {p['name']} ({p['strength']})")
            if p["reason"]:
                print(f"     Why: {p['reason'][:80]}...")
        
        print(f"\n🎯 Why This Matters:")
        for r in expl["whyThisMatters"]:
            print(f"  • {r}")
        
        print(f"\n📋 Learning Steps:")
        for step in expl["howToLearn"]:
            print(f"  {step['step']}. {step['action']}")
            print(f"     {step['details'][:100]}...")
        
        print(f"\n🎲 Suggested Activities:")
        for a in expl["suggestedActivities"]:
            print(f"  • {a}")
