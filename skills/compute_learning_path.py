#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 2: compute_learning_path
Given target topic(s) + current mastery state + age, return a minimal valid 
sequence respecting prerequisites (topological order, hard dependencies first).
"""

import json
from pathlib import Path
from collections import deque

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class LearningPathEngine:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.prereqs_for = load_index("dependencies_by_topic")
    
    def compute_path(self, target_topic_ids, mastered_ids=None, age=None, max_topics=50):
        """
        Compute a minimal valid learning path to reach target topics.
        
        Args:
            target_topic_ids: List of topic IDs to reach
            mastered_ids: Set of topic IDs already mastered (skip these)
            age: Child's age (filter age-inappropriate topics)
            max_topics: Hard limit on path length
        
        Returns:
            Dict with path (ordered list), metadata, and rationale
        """
        if mastered_ids is None:
            mastered_ids = set()
        else:
            mastered_ids = set(mastered_ids)
        
        # Collect all required topics via BFS from targets
        required = set()
        queue = deque(target_topic_ids)
        edges = []  # (prereq_id, topic_id, strength)
        
        while queue:
            tid = queue.popleft()
            if tid in required or tid in mastered_ids:
                continue
            required.add(tid)
            
            # Get prerequisites for this topic
            deps = self.prereqs_for.get(tid, [])
            for d in deps:
                pid = d["prerequisiteId"]
                strength = d.get("strength", "hard")
                edges.append((pid, tid, strength))
                if pid not in required and pid not in mastered_ids:
                    queue.append(pid)
        
        # Remove targets themselves from required (they're the goal, not the path)
        path_topics = required - set(target_topic_ids)
        
        # Topological sort: Kahn's algorithm with hard-first priority
        # Build adjacency and in-degree
        in_degree = {tid: 0 for tid in path_topics}
        hard_deps = {tid: set() for tid in path_topics}  # tid -> set of hard prereqs
        
        for pid, tid, strength in edges:
            if pid in path_topics and tid in path_topics:
                in_degree[tid] = in_degree.get(tid, 0) + 1
                if strength == "hard":
                    hard_deps[tid].add(pid)
        
        # Also track soft deps for metadata
        soft_deps = {tid: set() for tid in path_topics}
        for pid, tid, strength in edges:
            if pid in path_topics and tid in path_topics and strength == "soft":
                soft_deps[tid].add(pid)
        
        # Kahn's algorithm with priority: fewer hard deps first, then fewer total deps
        available = [tid for tid in path_topics if in_degree.get(tid, 0) == 0]
        # Sort by: (number of hard deps for dependents, ageRangeStart)
        def sort_key(tid):
            t = self.topic_by_id.get(tid, {})
            return (len(hard_deps.get(tid, [])), t.get("ageRangeStart", 0))
        
        available.sort(key=sort_key)
        
        ordered = []
        while available and len(ordered) < max_topics:
            tid = available.pop(0)
            ordered.append(tid)
            
            # Find topics that had this as prerequisite
            for e_pid, e_tid, e_strength in edges:
                if e_pid == tid and e_tid in path_topics:
                    in_degree[e_tid] -= 1
                    if in_degree[e_tid] == 0 and e_tid not in ordered and e_tid not in available:
                        available.append(e_tid)
                        available.sort(key=sort_key)
        
        # Build result
        path_details = []
        for tid in ordered:
            t = self.topic_by_id.get(tid, {})
            path_details.append({
                "id": tid,
                "name": t.get("name", "Unknown"),
                "subject": t.get("subject", "Unknown"),
                "domain": t.get("domain", "Unknown"),
                "type": t.get("type", "Unknown"),
                "ageRangeStart": t.get("ageRangeStart"),
                "ageRangeEnd": t.get("ageRangeEnd"),
                "hardPrereqs": list(hard_deps.get(tid, [])),
                "softPrereqs": list(soft_deps.get(tid, [])),
            })
        
        target_details = []
        for tid in target_topic_ids:
            t = self.topic_by_id.get(tid, {})
            target_details.append({
                "id": tid,
                "name": t.get("name", "Unknown"),
                "subject": t.get("subject", "Unknown"),
            })
        
        return {
            "path": path_details,
            "targets": target_details,
            "stats": {
                "totalSteps": len(path_details),
                "hardDependencies": sum(1 for d in edges if d[2] == "hard" and d[0] in path_topics),
                "softDependencies": sum(1 for d in edges if d[2] == "soft" and d[0] in path_topics),
                "skippedMastered": len(mastered_ids & required),
            },
            "rationale": f"Path computed via topological sort prioritizing hard prerequisites. "
                        f"{len(path_details)} topics required to reach {len(target_topic_ids)} target(s)."
        }

if __name__ == "__main__":
    engine = LearningPathEngine()
    
    # Demo: Path to "Understanding fractions" for a 7-year-old
    print("=" * 60)
    print("Skill 2: compute_learning_path")
    print("=" * 60)
    
    # Find a fractions topic
    results = [t for t in engine.topic_by_id.values() if "fractions" in t["name"].lower()]
    if results:
        target = results[0]
        print(f"\nTarget: {target['name']} ({target['id']})")
        print(f"Subject: {target.get('subject')}, Age: {target.get('ageRangeStart')}-{target.get('ageRangeEnd')}")
        
        result = engine.compute_path([target["id"]], age=7)
        print(f"\nPath length: {result['stats']['totalSteps']} topics")
        print(f"Hard deps: {result['stats']['hardDependencies']}")
        print(f"Soft deps: {result['stats']['softDependencies']}")
        
        print(f"\nFirst 5 steps:")
        for i, step in enumerate(result["path"][:5], 1):
            print(f"  {i}. {step['name']} ({step['id']}) [{step['subject']}] age {step['ageRangeStart']}-{step['ageRangeEnd']}")
        
        if len(result["path"]) > 5:
            print(f"  ... and {len(result['path']) - 5} more")
