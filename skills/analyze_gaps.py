#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 3: analyze_gaps
Given a target goal or set of topics + learner's current mastery,
return the minimal set of unmastered prerequisites prioritized by centrality/hardness.
"""

import json
from pathlib import Path
from collections import deque

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class GapAnalyzer:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.prereqs_for = load_index("dependencies_by_topic")
    
    def analyze_gaps(self, target_topic_ids, mastered_ids=None, in_progress_ids=None):
        """
        Analyze prerequisite gaps for reaching target topics.
        
        Args:
            target_topic_ids: List of topic IDs the learner wants to reach
            mastered_ids: Set of topic IDs already mastered
            in_progress_ids: Set of topic IDs currently being learned
        
        Returns:
            Dict with gap analysis, prioritized gaps, and metadata
        """
        if mastered_ids is None:
            mastered_ids = set()
        else:
            mastered_ids = set(mastered_ids)
        
        if in_progress_ids is None:
            in_progress_ids = set()
        else:
            in_progress_ids = set(in_progress_ids)
        
        # BFS to find all prerequisites
        all_required = set()
        queue = deque(target_topic_ids)
        edges = []
        
        while queue:
            tid = queue.popleft()
            if tid in all_required:
                continue
            all_required.add(tid)
            
            deps = self.prereqs_for.get(tid, [])
            for d in deps:
                pid = d["prerequisiteId"]
                strength = d.get("strength", "hard")
                edges.append((pid, tid, strength, d.get("reason", "")))
                if pid not in all_required:
                    queue.append(pid)
        
        # Categorize
        gaps = []
        already_mastered = []
        in_progress = []
        
        for tid in all_required:
            if tid in target_topic_ids:
                continue  # Don't count targets themselves as gaps
            
            t = self.topic_by_id.get(tid)
            if not t:
                continue
            
            if tid in mastered_ids:
                already_mastered.append({
                    "id": tid,
                    "name": t.get("name"),
                    "subject": t.get("subject"),
                    "centrality": t.get("centrality", 0),
                })
            elif tid in in_progress_ids:
                in_progress.append({
                    "id": tid,
                    "name": t.get("name"),
                    "subject": t.get("subject"),
                    "centrality": t.get("centrality", 0),
                })
            else:
                # This is a gap
                # Count how many hard deps it has (how foundational)
                hard_prereqs = sum(1 for e in edges if e[1] == tid and e[2] == "hard")
                soft_prereqs = sum(1 for e in edges if e[1] == tid and e[2] == "soft")
                
                # Get reasons for why this is needed
                reasons = [e[3] for e in edges if e[0] == tid and e[3]]
                
                gaps.append({
                    "id": tid,
                    "name": t.get("name"),
                    "subject": t.get("subject"),
                    "domain": t.get("domain"),
                    "type": t.get("type"),
                    "centrality": t.get("centrality", 0),
                    "ageRangeStart": t.get("ageRangeStart"),
                    "ageRangeEnd": t.get("ageRangeEnd"),
                    "hardPrereqCount": hard_prereqs,
                    "softPrereqCount": soft_prereqs,
                    "reasons": reasons[:3],  # Top 3 reasons
                    "assessmentPrompt": t.get("assessmentPrompt"),
                    "evidence": t.get("evidence", []),
                })
        
        # Sort gaps: hard prereqs first, then by centrality (desc), then age
        gaps.sort(key=lambda g: (
            -g["hardPrereqCount"],  # More dependents = more foundational
            -g["centrality"],        # Higher centrality = more important
            g.get("ageRangeStart", 0)  # Earlier age = more foundational
        ))
        
        # Identify critical path (hard gaps that block the most)
        critical_gaps = [g for g in gaps if g["hardPrereqCount"] > 0][:10]
        
        return {
            "gaps": gaps,
            "criticalGaps": critical_gaps,
            "stats": {
                "totalGaps": len(gaps),
                "criticalGaps": len(critical_gaps),
                "alreadyMastered": len(already_mastered),
                "inProgress": len(in_progress),
                "totalRequired": len(all_required),
            },
            "summary": f"Found {len(gaps)} gaps out of {len(all_required)} total prerequisites. "
                      f"{len(critical_gaps)} are on the critical path (blocking hard dependencies). "
                      f"{len(already_mastered)} already mastered, {len(in_progress)} in progress."
        }

if __name__ == "__main__":
    analyzer = GapAnalyzer()
    
    print("=" * 60)
    print("Skill 3: analyze_gaps")
    print("=" * 60)
    
    # Demo: Gaps for "Understanding fractions" assuming addition/subtraction mastered
    results = [t for t in analyzer.topic_by_id.values() if "fractions" in t["name"].lower()]
    if results:
        target = results[0]
        print(f"\nTarget: {target['name']} ({target['id']})")
        
        # Simulate: child has mastered basic addition
        mastered = set()
        for t in analyzer.topic_by_id.values():
            if "addition" in t["name"].lower() and t.get("ageRangeStart", 10) <= 6:
                mastered.add(t["id"])
        
        result = analyzer.analyze_gaps([target["id"]], mastered_ids=mastered)
        
        print(f"\n{result['summary']}")
        print(f"\nTop 5 Critical Gaps:")
        for i, gap in enumerate(result["gaps"][:5], 1):
            print(f"  {i}. {gap['name']} ({gap['id']})")
            print(f"     Subject: {gap['subject']}, Centrality: {gap['centrality']:.2f}, Hard deps: {gap['hardPrereqCount']}")
            if gap["reasons"]:
                print(f"     Why needed: {gap['reasons'][0][:80]}...")
