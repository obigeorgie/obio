#!/usr/bin/env python3
"""
MasteryGraph Core — Higher-Value Skill 2: Difficulty Estimator
Estimate topic difficulty using centrality + age + dependency depth + 
historical learner data.
"""

import json
from pathlib import Path

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class DifficultyEstimator:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.prereqs_for = load_index("dependencies_by_topic")
    
    def estimate_difficulty(self, topic_id, learner_age=None):
        """
        Estimate difficulty of a topic on a 1-10 scale.
        
        Factors:
        - centrality (higher = more foundational = technically easier conceptually but more important)
        - ageRange (older target age = harder)
        - dependency depth (more prerequisites = harder)
        - hard dependency ratio (more hard deps = harder)
        - topic type (PROCEDURAL slightly harder than CONCEPTUAL for young learners)
        
        Returns:
            Dict with difficulty score, factors, and interpretation
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        # Base factors
        centrality = topic.get("centrality", 0.5)
        age_start = topic.get("ageRangeStart", 6)
        age_end = topic.get("ageRangeEnd", 11)
        topic_type = topic.get("type", "CONCEPTUAL")
        
        # Dependency analysis
        deps = self.prereqs_for.get(topic_id, [])
        total_deps = len(deps)
        hard_deps = sum(1 for d in deps if d.get("strength") == "hard")
        soft_deps = total_deps - hard_deps
        
        # Calculate dependency depth (how many layers of prereqs)
        depth = self._calculate_prereq_depth(topic_id, visited=set())
        
        # Difficulty components (each 0-10)
        # Age factor: older target = harder (4-year-old content = 1, 11-year-old = 8)
        age_factor = min(10, max(1, (age_start - 3) * 1.2))
        
        # Dependency factor: more deps = harder
        dep_factor = min(10, total_deps * 0.8 + depth * 0.5)
        
        # Centrality factor: inverted — high centrality means foundational (easier conceptually)
        # but it's a bottleneck (harder to skip)
        centrality_factor = 5 - (centrality * 3)  # Lower centrality = higher difficulty
        centrality_factor = max(1, min(10, centrality_factor))
        
        # Type factor
        type_factor = 6 if topic_type == "PROCEDURAL" else (5 if topic_type == "CONCEPTUAL" else 4)
        
        # Hard dependency ratio
        hard_ratio = hard_deps / total_deps if total_deps > 0 else 0
        hardness_factor = 3 + hard_ratio * 5
        
        # Weighted composite
        difficulty = (
            age_factor * 0.30 +
            dep_factor * 0.25 +
            centrality_factor * 0.15 +
            type_factor * 0.15 +
            hardness_factor * 0.15
        )
        
        difficulty = round(max(1, min(10, difficulty)), 1)
        
        # Age appropriateness check
        age_appropriate = True
        if learner_age and learner_age < age_start - 1:
            age_appropriate = False
        
        return {
            "topicId": topic_id,
            "topicName": topic.get("name"),
            "difficultyScore": difficulty,
            "interpretation": self._interpret_score(difficulty),
            "ageAppropriate": age_appropriate,
            "targetAge": f"{age_start}-{age_end}",
            "factors": {
                "ageFactor": round(age_factor, 1),
                "dependencyFactor": round(dep_factor, 1),
                "centralityFactor": round(centrality_factor, 1),
                "typeFactor": type_factor,
                "hardnessFactor": round(hardness_factor, 1),
            },
            "dependencies": {
                "total": total_deps,
                "hard": hard_deps,
                "soft": soft_deps,
                "depth": depth,
            }
        }
    
    def _calculate_prereq_depth(self, topic_id, visited=None):
        """Calculate max prerequisite depth."""
        if visited is None:
            visited = set()
        if topic_id in visited:
            return 0
        visited.add(topic_id)
        
        deps = self.prereqs_for.get(topic_id, [])
        if not deps:
            return 0
        
        max_depth = 0
        for d in deps:
            pid = d["prerequisiteId"]
            if pid not in visited:
                depth = self._calculate_prereq_depth(pid, visited.copy())
                max_depth = max(max_depth, depth + 1)
        
        return max_depth
    
    def _interpret_score(self, score):
        """Human-readable interpretation."""
        if score <= 3:
            return "Foundation level — accessible with minimal prerequisites"
        elif score <= 5:
            return "Intermediate — requires solid foundations but achievable with support"
        elif score <= 7:
            return "Advanced — multiple prerequisites, requires sustained effort"
        else:
            return "Expert — deep prerequisite chain, mastery of fundamentals essential"
    
    def rank_topics_by_difficulty(self, topic_ids, learner_age=None):
        """Rank a list of topics by estimated difficulty."""
        results = []
        for tid in topic_ids:
            est = self.estimate_difficulty(tid, learner_age)
            if "error" not in est:
                results.append(est)
        
        results.sort(key=lambda x: x["difficultyScore"], reverse=True)
        return results
    
    def estimate_path_difficulty(self, path_topic_ids, learner_age=None):
        """Estimate cumulative difficulty of a learning path."""
        estimates = [self.estimate_difficulty(tid, learner_age) for tid in path_topic_ids]
        estimates = [e for e in estimates if "error" not in e]
        
        if not estimates:
            return {"error": "No valid topics in path"}
        
        scores = [e["difficultyScore"] for e in estimates]
        return {
            "pathLength": len(estimates),
            "avgDifficulty": round(sum(scores) / len(scores), 1),
            "maxDifficulty": max(scores),
            "minDifficulty": min(scores),
            "progression": [e["difficultyScore"] for e in estimates],
            "hardestTopic": max(estimates, key=lambda x: x["difficultyScore"]),
            "easiestTopic": min(estimates, key=lambda x: x["difficultyScore"]),
        }

if __name__ == "__main__":
    est = DifficultyEstimator()
    
    print("=" * 60)
    print("Higher-Value Skill 2: Difficulty Estimator")
    print("=" * 60)
    
    # Demo: Compare difficulties of various topics
    test_queries = ["fractions", "counting", "addition", "multiplication", "algebra"]
    
    print(f"\n📊 Difficulty Comparison (for age 7 learner):")
    print(f"{'Topic':<40} {'Score':<8} {'Interpretation':<50}")
    print("-" * 100)
    
    for q in test_queries:
        results = [t for t in est.topic_by_id.values() if q in t["name"].lower()]
        if results:
            t = results[0]
            diff = est.estimate_difficulty(t["id"], learner_age=7)
            print(f"{diff['topicName'][:38]:<40} {diff['difficultyScore']:<8} {diff['interpretation']:<50}")
    
    # Demo: Path difficulty
    print(f"\n🛤️ Path Difficulty Analysis:")
    path = [t["id"] for t in est.topic_by_id.values() if "fractions" in t["name"].lower()][:5]
    if path:
        path_diff = est.estimate_path_difficulty(path, learner_age=7)
        print(f"  Path length: {path_diff['pathLength']}")
        print(f"  Average difficulty: {path_diff['avgDifficulty']}")
        print(f"  Hardest: {path_diff['hardestTopic']['topicName']} ({path_diff['maxDifficulty']})")
        print(f"  Easiest: {path_diff['easiestTopic']['topicName']} ({path_diff['minDifficulty']})")
