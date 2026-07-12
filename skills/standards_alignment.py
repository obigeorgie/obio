#!/usr/bin/env python3
"""
MasteryGraph Core — Higher-Value Skill 1: Standards Alignment Reporter
Map topics to curriculum standards (CCSS, NGSS, IB, etc.) and generate
alignment reports for schools, homeschool parents, or portfolio documentation.
"""

import json
from pathlib import Path
from collections import defaultdict

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class StandardsAligner:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        # Load raw curriculum standards
        raw_path = Path("/root/.openclaw/workspace/marble-taxonomy/data/curriculum-standards.json")
        with open(raw_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.curricula = data.get("curricula", [])
        # Build searchable index of standards
        self.standards_index = []
        for curr in self.curricula:
            curr_name = curr.get("name", "Unknown")
            curr_slug = curr.get("slug", "")
            for std_topic in curr.get("topics", []):
                std_data = std_topic.get("data", {})
                self.standards_index.append({
                    "_curriculum": curr_name,
                    "_slug": curr_slug,
                    "key": std_topic.get("key"),
                    "code": std_topic.get("code"),
                    "title": std_data.get("title", ""),
                    "subject": std_data.get("subject", ""),
                    "domain": std_data.get("domain", ""),
                    "description": std_data.get("description", ""),
                    "gradeLevel": std_data.get("keyStage", ""),
                })
    
    def _normalize_subject(self, subject):
        """Normalize subject names for matching."""
        mapping = {
            "mathematics": "Mathematics",
            "math": "Mathematics",
            "maths": "Mathematics",
            "english language arts": "English",
            "english": "English",
            "science": "Science",
            "history": "History",
            "social studies": "History",
            "computing": "Computing",
            "computer science": "Computing",
        }
        return mapping.get(subject.lower(), subject)
    
    def align_topic_to_standards(self, topic_id):
        """
        Find curriculum standards that align with a given topic.
        Uses fuzzy matching by subject, domain keywords, and age range.
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        topic_subject = self._normalize_subject(topic.get("subject", ""))
        topic_domain = topic.get("domain", "").lower()
        topic_name = topic.get("name", "").lower()
        topic_age_start = topic.get("ageRangeStart", 0)
        topic_age_end = topic.get("ageRangeEnd", 18)
        topic_desc = topic.get("description", "").lower()
        
        matches = []
        for std in self.standards_index:
            std_subject = self._normalize_subject(std.get("subject", ""))
            std_title = std.get("title", "").lower()
            std_desc = std.get("description", "").lower()
            
            # Subject match
            subject_match = (std_subject == topic_subject or 
                           std_subject.lower() in topic_subject.lower() or
                           topic_subject.lower() in std_subject.lower())
            
            if not subject_match:
                continue
            
            # Keyword overlap scoring
            keywords = set(topic_name.split() + topic_desc.split() + topic_domain.split())
            std_text = std_title + " " + std_desc
            std_words = set(std_text.split())
            overlap = len(keywords & std_words)
            
            # Age appropriateness (rough mapping from keyStage to age)
            grade = std.get("gradeLevel", "").lower()
            age_approx = 0
            if "key stage 1" in grade or "grade 1" in grade or "grade 2" in grade:
                age_approx = 6
            elif "key stage 2" in grade or "grade 3" in grade or "grade 4" in grade:
                age_approx = 9
            elif "grade 5" in grade or "grade 6" in grade:
                age_approx = 11
            elif "middle" in grade:
                age_approx = 13
            
            age_match = abs(age_approx - topic_age_start) <= 3
            
            if overlap >= 2 or age_match:
                matches.append({
                    "standard": std,
                    "overlapScore": overlap,
                    "ageMatch": age_match,
                })
        
        # Sort by overlap score
        matches.sort(key=lambda x: (-x["overlapScore"], not x["ageMatch"]))
        
        return {
            "topicId": topic_id,
            "topicName": topic.get("name"),
            "alignedStandards": [
                {
                    "curriculum": m["standard"]["_curriculum"],
                    "code": m["standard"]["code"],
                    "title": m["standard"]["title"],
                    "description": m["standard"]["description"][:150],
                    "gradeLevel": m["standard"]["gradeLevel"],
                    "overlapScore": m["overlapScore"],
                }
                for m in matches[:10]
            ],
            "matchCount": len(matches),
        }
    
    def align_path_to_standards(self, topic_ids):
        """
        Given a learning path, return aligned standards by curriculum.
        """
        aligned = {}
        topic_coverage = {}
        
        for tid in topic_ids:
            result = self.align_topic_to_standards(tid)
            if "error" in result:
                continue
            
            topic_coverage[tid] = {
                "name": result["topicName"],
                "standardsCount": result["matchCount"],
            }
            
            for std in result["alignedStandards"]:
                curr = std["curriculum"]
                if curr not in aligned:
                    aligned[curr] = []
                aligned[curr].append({
                    "topicId": tid,
                    "topicName": result["topicName"],
                    "standardCode": std["code"],
                    "title": std["title"],
                    "gradeLevel": std["gradeLevel"],
                })
        
        # Deduplicate
        for curr in aligned:
            seen = set()
            unique = []
            for item in aligned[curr]:
                key = (item["topicId"], item["standardCode"])
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            aligned[curr] = unique
        
        return {
            "byCurriculum": aligned,
            "topicCoverage": topic_coverage,
            "summary": {
                "totalTopics": len(topic_ids),
                "topicsWithStandards": sum(1 for t in topic_coverage.values() if t["standardsCount"] > 0),
                "totalStandardsCovered": sum(len(v) for v in aligned.values()),
                "curriculaCovered": list(aligned.keys()),
            }
        }
    
    def generate_portfolio_report(self, learner_id, mastered_ids, in_progress_ids=None):
        """
        Generate a standards-aligned portfolio report.
        """
        if in_progress_ids is None:
            in_progress_ids = []
        
        all_ids = list(mastered_ids) + list(in_progress_ids)
        alignment = self.align_path_to_standards(all_ids)
        
        report = {
            "learnerId": learner_id,
            "masteredTopics": len(mastered_ids),
            "inProgressTopics": len(in_progress_ids),
            "standardsAlignment": alignment,
            "curriculumCoverage": []
        }
        
        for curr_name, standards in alignment["byCurriculum"].items():
            seen_codes = set()
            unique_codes = []
            for s in standards:
                if s["standardCode"] not in seen_codes:
                    seen_codes.add(s["standardCode"])
                    unique_codes.append(s["standardCode"])
            
            mastered_count = sum(1 for s in standards if s["topicId"] in mastered_ids)
            
            report["curriculumCoverage"].append({
                "curriculum": curr_name,
                "totalAlignedStandards": len(unique_codes),
                "sampleStandards": unique_codes[:10],
                "masteryEvidence": f"Demonstrated through {mastered_count} mastered topics",
            })
        
        return report
    
    def find_topics_by_standard(self, standard_code):
        """Find topics that might align with a standard code."""
        results = []
        for tid, topic in self.topic_by_id.items():
            alignment = self.align_topic_to_standards(tid)
            for std in alignment.get("alignedStandards", []):
                if std["code"] == standard_code:
                    results.append({
                        "topicId": tid,
                        "topicName": topic.get("name"),
                        "standardCode": standard_code,
                        "curriculum": std["curriculum"],
                    })
        return results[:20]

if __name__ == "__main__":
    aligner = StandardsAligner()
    
    print("=" * 60)
    print("Higher-Value Skill 1: Standards Alignment Reporter")
    print("=" * 60)
    
    # Show available curricula
    print(f"\n📚 Curricula indexed:")
    for curr in aligner.curricula:
        print(f"  • {curr.get('name')} ({curr.get('slug')}) — {len(curr.get('topics', []))} standards")
    
    # Demo: Align a fractions topic
    results = [t for t in aligner.topic_by_id.values() if "fractions" in t["name"].lower()]
    if results:
        target = results[0]
        print(f"\n🎯 Topic: {target['name']} ({target['id']})")
        
        alignment = aligner.align_topic_to_standards(target["id"])
        print(f"  Aligned standards: {alignment['matchCount']}")
        for std in alignment["alignedStandards"][:5]:
            print(f"    • {std['code']} ({std['curriculum'][:30]}...)")
            print(f"      {std['title'][:60]}...")
        
        # Full path alignment
        full = aligner.align_path_to_standards([target["id"]])
        print(f"\n  Curricula covered: {full['summary']['curriculaCovered']}")
        print(f"  Topics with standards: {full['summary']['topicsWithStandards']}")