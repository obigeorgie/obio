#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 8: cluster_summary
Use clusters.json to generate parent-friendly progress reports 
and "what to focus on next" summaries.
"""

import json
from pathlib import Path
from collections import defaultdict

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class ClusterSummarizer:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.clusters = load_index("clusters")
        self.topics_by_subject = load_index("topics_by_subject")
    
    def get_all_clusters(self):
        """Return all cluster summaries."""
        return self.clusters
    
    def get_clusters_by_subject(self, subject):
        """Get clusters for a specific subject."""
        return [c for c in self.clusters if c.get("subject") == subject]
    
    def get_clusters_by_age(self, age):
        """Get clusters appropriate for a given age."""
        return [c for c in self.clusters 
                if c.get("ageRangeStart", 0) <= age <= c.get("ageRangeEnd", 18)]
    
    def generate_progress_report(self, learner_id, mastered_ids, in_progress_ids=None):
        """
        Generate a parent-friendly progress report based on cluster coverage.
        
        Args:
            learner_id: Learner ID
            mastered_ids: List of mastered topic IDs
            in_progress_ids: List of in-progress topic IDs
        
        Returns:
            Dict with cluster coverage, strengths, gaps, and next focus
        """
        if in_progress_ids is None:
            in_progress_ids = []
        
        mastered_set = set(mastered_ids)
        in_progress_set = set(in_progress_ids)
        
        # Map topics to clusters (approximate by subject + domain + age)
        cluster_coverage = []
        
        for cluster in self.clusters:
            # Find topics in this cluster's subject/domain/age range
            subject = cluster.get("subject", "")
            domain = cluster.get("domain", "")
            age_start = cluster.get("ageRangeStart", 0)
            age_end = cluster.get("ageRangeEnd", 18)
            
            # Get topics matching this cluster
            matching_topics = []
            for t in self.topic_by_id.values():
                if (t.get("subject") == subject and 
                    t.get("domain") == domain and
                    age_start <= t.get("ageRangeStart", 0) <= age_end):
                    matching_topics.append(t)
            
            if not matching_topics:
                continue
            
            mastered_in_cluster = sum(1 for t in matching_topics if t["id"] in mastered_set)
            in_progress_in_cluster = sum(1 for t in matching_topics if t["id"] in in_progress_set)
            total = len(matching_topics)
            
            coverage = mastered_in_cluster / total if total > 0 else 0
            
            cluster_coverage.append({
                "cluster": cluster,
                "totalTopics": total,
                "mastered": mastered_in_cluster,
                "inProgress": in_progress_in_cluster,
                "coverage": coverage,
                "status": "completed" if coverage >= 0.8 else ("in-progress" if coverage >= 0.3 else "not-started"),
            })
        
        # Sort by coverage
        cluster_coverage.sort(key=lambda x: x["coverage"], reverse=True)
        
        # Identify strengths and gaps
        strengths = [c for c in cluster_coverage if c["status"] == "completed"]
        gaps = [c for c in cluster_coverage if c["status"] == "not-started"]
        in_progress_clusters = [c for c in cluster_coverage if c["status"] == "in-progress"]
        
        # Recommend next focus
        recommendations = []
        
        # Priority 1: Complete in-progress clusters
        for c in in_progress_clusters[:3]:
            recommendations.append({
                "priority": 1,
                "cluster": c["cluster"],
                "action": f"Continue working on {c['cluster']['domain']} — {c['inProgress']} topic(s) in progress",
                "reason": "Almost there! Finishing these will unlock more advanced topics.",
            })
        
        # Priority 2: Start foundational gaps
        for c in gaps[:3]:
            recommendations.append({
                "priority": 2,
                "cluster": c["cluster"],
                "action": f"Begin exploring {c['cluster']['domain']}",
                "reason": f"{c['cluster']['summary'][:100]}...",
            })
        
        # Build parent-friendly summary
        summary = {
            "learnerId": learner_id,
            "overallStats": {
                "totalClustersTracked": len(cluster_coverage),
                "completedClusters": len(strengths),
                "inProgressClusters": len(in_progress_clusters),
                "notStartedClusters": len(gaps),
                "overallCoverage": sum(c["coverage"] for c in cluster_coverage) / len(cluster_coverage) if cluster_coverage else 0,
            },
            "strengths": [
                {
                    "subject": c["cluster"]["subject"],
                    "domain": c["cluster"]["domain"],
                    "summary": c["cluster"].get("summary", ""),
                    "coverage": f"{c['coverage']*100:.0f}%",
                }
                for c in strengths[:5]
            ],
            "gaps": [
                {
                    "subject": c["cluster"]["subject"],
                    "domain": c["cluster"]["domain"],
                    "summary": c["cluster"].get("summary", ""),
                    "ageRange": f"{c['cluster'].get('ageRangeStart')}-{c['cluster'].get('ageRangeEnd')}",
                }
                for c in gaps[:5]
            ],
            "recommendations": recommendations,
            "parentFriendlySummary": self._generate_parent_summary(strengths, gaps, in_progress_clusters),
        }
        
        return summary
    
    def _generate_parent_summary(self, strengths, gaps, in_progress):
        """Generate a warm, parent-friendly text summary."""
        lines = []
        
        if strengths:
            lines.append(f"🌟 **Strengths:** Your child is doing great in {len(strengths)} area(s), including " +
                        ", ".join(s["cluster"]["domain"] for s in strengths[:3]) + ".")
        
        if in_progress:
            lines.append(f"🚧 **In Progress:** They're actively learning {len(in_progress)} topic cluster(s). " +
                        "Keep up the great work!")
        
        if gaps:
            lines.append(f"🎯 **Next Steps:** {len(gaps)} area(s) ready to explore when they're ready, " +
                        f"starting with {gaps[0]['cluster']['domain']}.")
        
        lines.append("\nRemember: Every child learns at their own pace. The graph ensures we build " +
                    "foundations before advancing. No gaps = no struggles later.")
        
        return "\n\n".join(lines)
    
    def get_cluster_detail(self, subject, domain):
        """Get detailed info about a specific cluster."""
        for c in self.clusters:
            if c.get("subject") == subject and c.get("domain") == domain:
                return c
        return None

if __name__ == "__main__":
    summarizer = ClusterSummarizer()
    
    print("=" * 60)
    print("Skill 8: cluster_summary")
    print("=" * 60)
    
    # Demo: Show available clusters
    print(f"\nTotal clusters: {len(summarizer.clusters)}")
    
    # Show by subject
    subjects = defaultdict(int)
    for c in summarizer.clusters:
        subjects[c.get("subject", "Unknown")] += 1
    
    print(f"\nClusters by subject:")
    for subj, count in sorted(subjects.items(), key=lambda x: -x[1]):
        print(f"  {subj}: {count}")
    
    # Show a sample cluster
    if summarizer.clusters:
        sample = summarizer.clusters[0]
        print(f"\n📋 Sample cluster:")
        print(f"  Subject: {sample.get('subject')}")
        print(f"  Domain: {sample.get('domain')}")
        print(f"  Age: {sample.get('ageRangeStart')}-{sample.get('ageRangeEnd')}")
        print(f"  Summary: {sample.get('summary', '')[:150]}...")
    
    # Demo: Generate a progress report with some mastered topics
    print(f"\n📊 Demo Progress Report:")
    
    # Simulate some mastered math topics
    math_topics = [t for t in summarizer.topic_by_id.values() if t.get("subject") == "Mathematics"]
    mastered = [t["id"] for t in math_topics[:50]]  # Pretend they mastered 50 math topics
    
    report = summarizer.generate_progress_report("demo_child", mastered)
    
    print(f"  Overall coverage: {report['overallStats']['overallCoverage']*100:.1f}%")
    print(f"  Completed clusters: {report['overallStats']['completedClusters']}")
    print(f"  In progress: {report['overallStats']['inProgressClusters']}")
    print(f"  Not started: {report['overallStats']['notStartedClusters']}")
    
    print(f"\n  Top recommendation:")
    if report["recommendations"]:
        rec = report["recommendations"][0]
        print(f"    {rec['action']}")
        print(f"    Why: {rec['reason'][:100]}...")
    
    print(f"\n{report['parentFriendlySummary'][:300]}...")
