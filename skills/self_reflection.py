#!/usr/bin/env python3
"""
MasteryGraph Core — Higher-Value Skill 4: Self-Reflection & Skill Improver
Analyze skill performance, learner outcomes, and system behavior to improve
recommendations over time. Meta-skill for continuous improvement.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROFILE_DIR = Path("/root/.openclaw/workspace/masterygraph-profiles")
LOG_DIR = Path("/root/.openclaw/workspace/masterygraph-logs")
LOG_DIR.mkdir(exist_ok=True)

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class SelfReflectionEngine:
    """
    Meta-skill: observes how learners progress, what paths work,
    where diagnostics fail, and improves recommendations.
    """
    
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.prereqs_for = load_index("dependencies_by_topic")
    
    def _log_event(self, event_type, data):
        """Log a system event for later analysis."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
        }
        log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + "\n")
    
    def log_diagnostic_result(self, learner_id, topic_id, format_type, score, passed):
        """Log diagnostic outcome for analysis."""
        self._log_event("diagnostic_result", {
            "learnerId": learner_id,
            "topicId": topic_id,
            "format": format_type,
            "score": score,
            "passed": passed,
        })
    
    def log_path_completion(self, learner_id, path, completion_rate, time_spent):
        """Log how well a learning path worked."""
        self._log_event("path_completion", {
            "learnerId": learner_id,
            "pathLength": len(path),
            "completionRate": completion_rate,
            "timeSpentMinutes": time_spent,
            "topicIds": path,
        })
    
    def log_mastery_update(self, learner_id, topic_id, old_status, new_status, confidence):
        """Log mastery transitions."""
        self._log_event("mastery_transition", {
            "learnerId": learner_id,
            "topicId": topic_id,
            "oldStatus": old_status,
            "newStatus": new_status,
            "confidence": confidence,
        })
    
    def analyze_learner_patterns(self, learner_id):
        """
        Analyze a learner's history to identify patterns and optimize future paths.
        
        Returns insights like:
        - Fastest mastered topics (strengths)
        - Topics that took longest (potential struggle areas)
        - Success rate by topic type
        - Optimal session length
        """
        profile_path = PROFILE_DIR / f"{learner_id}.json"
        if not profile_path.exists():
            return {"error": f"No profile found for {learner_id}"}
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        mastery = profile.get("masteryMap", {})
        diagnostics = profile.get("diagnostics", [])
        
        # Analyze by topic type
        by_type = defaultdict(lambda: {"count": 0, "totalConfidence": 0, "mastered": 0})
        for tid, data in mastery.items():
            topic = self.topic_by_id.get(tid, {})
            ttype = topic.get("type", "UNKNOWN")
            by_type[ttype]["count"] += 1
            by_type[ttype]["totalConfidence"] += data.get("confidence", 0) or 0
            if data.get("status") == "mastered":
                by_type[ttype]["mastered"] += 1
        
        # Analyze by subject
        by_subject = defaultdict(lambda: {"count": 0, "mastered": 0})
        for tid, data in mastery.items():
            topic = self.topic_by_id.get(tid, {})
            subj = topic.get("subject", "Unknown")
            by_subject[subj]["count"] += 1
            if data.get("status") == "mastered":
                by_subject[subj]["mastered"] += 1
        
        # Calculate mastery rates
        for ttype in by_type:
            count = by_type[ttype]["count"]
            by_type[ttype]["masteryRate"] = round(by_type[ttype]["mastered"] / count, 2) if count > 0 else 0
            by_type[ttype]["avgConfidence"] = round(by_type[ttype]["totalConfidence"] / count, 2) if count > 0 else 0
        
        for subj in by_subject:
            count = by_subject[subj]["count"]
            by_subject[subj]["masteryRate"] = round(by_subject[subj]["mastered"] / count, 2) if count > 0 else 0
        
        # Find strongest subject
        strongest = max(by_subject.items(), key=lambda x: x[1]["masteryRate"]) if by_subject else (None, {})
        weakest = min(by_subject.items(), key=lambda x: x[1]["masteryRate"]) if by_subject else (None, {})
        
        # Diagostic accuracy analysis
        diag_by_format = defaultdict(lambda: {"total": 0, "passed": 0})
        for d in diagnostics:
            fmt = d.get("format", "unknown")
            diag_by_format[fmt]["total"] += 1
            if d.get("results", {}).get("passed", False):
                diag_by_format[fmt]["passed"] += 1
        
        for fmt in diag_by_format:
            total = diag_by_format[fmt]["total"]
            diag_by_format[fmt]["passRate"] = round(diag_by_format[fmt]["passed"] / total, 2) if total > 0 else 0
        
        return {
            "learnerId": learner_id,
            "totalTopicsAttempted": len(mastery),
            "totalMastered": sum(1 for d in mastery.values() if d.get("status") == "mastered"),
            "byType": dict(by_type),
            "bySubject": dict(by_subject),
            "strongestSubject": {"subject": strongest[0], **strongest[1]} if strongest[0] else None,
            "weakestSubject": {"subject": weakest[0], **weakest[1]} if weakest[0] else None,
            "diagnosticEffectiveness": dict(diag_by_format),
            "recommendations": self._generate_recommendations(by_type, by_subject, strongest, weakest),
        }
    
    def _generate_recommendations(self, by_type, by_subject, strongest, weakest):
        """Generate personalized recommendations based on pattern analysis."""
        recs = []
        
        # Subject-level recommendations
        if strongest[0] and strongest[1].get("masteryRate", 0) > 0.7:
            recs.append({
                "type": "strength",
                "message": f"Learner shows strong mastery in {strongest[0]}. "
                          f"Consider accelerating or offering enrichment.",
            })
        
        if weakest[0] and weakest[1].get("masteryRate", 0) < 0.4:
            recs.append({
                "type": "intervention",
                "message": f"Struggling with {weakest[0]}. Consider: "
                          f"1) More visual scaffolding, 2) Shorter sessions, 3) Prerequisite review.",
            })
        
        # Type-level recommendations
        for ttype, data in by_type.items():
            if data["count"] >= 3 and data["masteryRate"] < 0.3:
                recs.append({
                    "type": "format_adjustment",
                    "message": f"Low mastery rate for {ttype} topics ({data['masteryRate']*100:.0f}%). "
                              f"Consider changing diagnostic format or adding more scaffolding.",
                })
        
        return recs
    
    def analyze_system_patterns(self):
        """
        Analyze system-wide patterns across all learners.
        
        Returns:
            Dict with system-wide insights
        """
        # Collect all logs
        all_logs = []
        for log_file in LOG_DIR.glob("*.jsonl"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        all_logs.append(json.loads(line))
                    except:
                        pass
        
        if not all_logs:
            return {"message": "No logs yet. Start using the system to generate data."}
        
        # Analyze by event type
        by_type = defaultdict(list)
        for log in all_logs:
            by_type[log.get("type")].append(log)
        
        # Diagnostic effectiveness
        diag_results = by_type.get("diagnostic_result", [])
        pass_rate = sum(1 for d in diag_results if d["data"].get("passed")) / len(diag_results) if diag_results else 0
        
        # Format effectiveness
        format_pass = defaultdict(lambda: {"total": 0, "passed": 0})
        for d in diag_results:
            fmt = d["data"].get("format", "unknown")
            format_pass[fmt]["total"] += 1
            if d["data"].get("passed"):
                format_pass[fmt]["passed"] += 1
        
        for fmt in format_pass:
            total = format_pass[fmt]["total"]
            format_pass[fmt]["rate"] = round(format_pass[fmt]["passed"] / total, 2) if total > 0 else 0
        
        # Path completion rates
        path_logs = by_type.get("path_completion", [])
        avg_completion = sum(p["data"].get("completionRate", 0) for p in path_logs) / len(path_logs) if path_logs else 0
        
        return {
            "totalEvents": len(all_logs),
            "diagnostics": {
                "total": len(diag_results),
                "overallPassRate": round(pass_rate, 2),
                "byFormat": dict(format_pass),
            },
            "paths": {
                "total": len(path_logs),
                "avgCompletionRate": round(avg_completion, 2),
            },
            "systemRecommendations": self._generate_system_recommendations(format_pass, avg_completion),
        }
    
    def _generate_system_recommendations(self, format_pass, avg_completion):
        """Generate system-level improvement recommendations."""
        recs = []
        
        # Find best performing format
        if format_pass:
            best = max(format_pass.items(), key=lambda x: x[1].get("rate", 0))
            worst = min(format_pass.items(), key=lambda x: x[1].get("rate", 0))
            recs.append({
                "type": "format_optimization",
                "message": f"Best diagnostic format: {best[0]} ({best[1]['rate']*100:.0f}% pass rate). "
                          f"Worst: {worst[0]} ({worst[1]['rate']*100:.0f}%). "
                          f"Consider promoting {best[0]} for similar topics.",
            })
        
        if avg_completion < 0.5:
            recs.append({
                "type": "path_length",
                "message": f"Low path completion rate ({avg_completion*100:.0f}%). "
                          f"Consider shortening paths or adding more checkpoints.",
            })
        
        return recs
    
    def suggest_skill_improvements(self):
        """
        Suggest improvements to the skills themselves based on observed data.
        """
        system_analysis = self.analyze_system_patterns()
        
        improvements = []
        
        # Check if we have enough data
        if system_analysis.get("totalEvents", 0) < 10:
            improvements.append({
                "area": "data_collection",
                "message": "Need more learner interactions to make meaningful improvements. "
                          "Continue using the system.",
                "priority": "low",
            })
            return improvements
        
        # Analyze format effectiveness
        by_format = system_analysis.get("diagnostics", {}).get("byFormat", {})
        for fmt, data in by_format.items():
            if data.get("rate", 1) < 0.3:
                improvements.append({
                    "area": "diagnostic_generation",
                    "message": f"Diagnostic format '{fmt}' has low pass rate. "
                              f"Review question quality and age-appropriateness.",
                    "priority": "high",
                })
        
        # Path completion analysis
        if system_analysis.get("paths", {}).get("avgCompletionRate", 1) < 0.5:
            improvements.append({
                "area": "path_computation",
                "message": "Paths too long or poorly sequenced. Consider: "
                          "1) Smaller chunks, 2) More frequent mastery checks, 3) Better gap prioritization.",
                "priority": "high",
            })
        
        return improvements

if __name__ == "__main__":
    engine = SelfReflectionEngine()
    
    print("=" * 60)
    print("Higher-Value Skill 4: Self-Reflection & Skill Improver")
    print("=" * 60)
    
    # Log some demo events
    print("\n📝 Logging demo events...")
    engine.log_diagnostic_result("demo_child_001", "mt_yJmvUCCym7", "quiz", 0.8, True)
    engine.log_diagnostic_result("demo_child_001", "mt_IHipFGTFEY", "quiz", 0.3, False)
    engine.log_mastery_update("demo_child_001", "mt_yJmvUCCym7", "not-started", "mastered", 0.9)
    engine.log_mastery_update("demo_child_001", "mt_IHipFGTFEY", "not-started", "in-progress", 0.4)
    
    # Analyze learner patterns
    print("\n🔍 Learner Pattern Analysis:")
    analysis = engine.analyze_learner_patterns("demo_child_001")
    print(f"  Total topics: {analysis['totalTopicsAttempted']}")
    print(f"  Mastered: {analysis['totalMastered']}")
    if analysis.get('strongestSubject'):
        print(f"  Strongest: {analysis['strongestSubject']['subject']} "
              f"({analysis['strongestSubject'].get('masteryRate', 0)*100:.0f}%)")
    if analysis.get('weakestSubject'):
        print(f"  Weakest: {analysis['weakestSubject']['subject']} "
              f"({analysis['weakestSubject'].get('masteryRate', 0)*100:.0f}%)")
    
    print(f"\n📊 Recommendations:")
    for rec in analysis.get("recommendations", []):
        print(f"  [{rec['type']}] {rec['message']}")
    
    # System analysis
    print(f"\n🌐 System-Wide Analysis:")
    sys = engine.analyze_system_patterns()
    print(f"  Total events: {sys.get('totalEvents', 0)}")
    print(f"  Diagnostic pass rate: {sys.get('diagnostics', {}).get('overallPassRate', 0)*100:.0f}%")
    
    # Skill improvement suggestions
    print(f"\n🔧 Skill Improvement Suggestions:")
    improvements = engine.suggest_skill_improvements()
    for imp in improvements:
        print(f"  [{imp['priority']}] {imp['area']}: {imp['message']}")
    
    print(f"\n✅ Self-reflection engine active and logging")
