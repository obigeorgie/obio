#!/usr/bin/env python3
"""
MasteryGraph Core — Master Orchestrator
Ties all skills together into a unified interface.
"""

import json
import sys
from pathlib import Path

# Add skills directory
sys.path.insert(0, str(Path(__file__).parent / "skills"))

from compute_learning_path import LearningPathEngine
from analyze_gaps import GapAnalyzer
from generate_diagnostic import DiagnosticGenerator
from generate_grounded_explanation import ExplanationEngine
from update_learner_profile import LearnerProfileManager
from create_personalized_plan import PlanGenerator
from cluster_summary import ClusterSummarizer
from standards_alignment import StandardsAligner
from difficulty_estimator import DifficultyEstimator
from content_request_router import ContentRouter
from self_reflection import SelfReflectionEngine

class MasteryGraphCore:
    """Unified interface for all MasteryGraph Core capabilities."""
    
    def __init__(self):
        self.path_engine = LearningPathEngine()
        self.gap_analyzer = GapAnalyzer()
        self.diagnostic_gen = DiagnosticGenerator()
        self.explanation_engine = ExplanationEngine()
        self.profile_mgr = LearnerProfileManager()
        self.plan_gen = PlanGenerator()
        self.cluster_summarizer = ClusterSummarizer()
        self.standards_aligner = StandardsAligner()
        self.difficulty_est = DifficultyEstimator()
        self.content_router = ContentRouter()
        self.reflection = SelfReflectionEngine()
    
    # === Core Skills (1-8) ===
    def get_topic(self, topic_id):
        """Get topic by ID."""
        return self.path_engine.topic_by_id.get(topic_id)
    
    def search_topics(self, query):
        """Search topics by name."""
        query = query.lower()
        return [t for t in self.path_engine.topic_by_id.values() if query in t["name"].lower()]
    
    def compute_path(self, target_topic_ids, mastered_ids=None, age=None):
        """Compute learning path to target topics."""
        return self.path_engine.compute_path(target_topic_ids, mastered_ids, age)
    
    def analyze_gaps(self, target_topic_ids, mastered_ids=None, in_progress_ids=None):
        """Analyze prerequisite gaps."""
        return self.gap_analyzer.analyze_gaps(target_topic_ids, mastered_ids, in_progress_ids)
    
    def generate_diagnostic(self, topic_id, format="auto", age=None):
        """Generate diagnostic for a topic."""
        return self.diagnostic_gen.generate_diagnostic(topic_id, format, age)
    
    def explain(self, topic_id, depth=2, age=None):
        """Generate grounded explanation."""
        return self.explanation_engine.explain(topic_id, depth, age)
    
    def create_profile(self, learner_id, **kwargs):
        """Create learner profile."""
        return self.profile_mgr.create_profile(learner_id, **kwargs)
    
    def update_mastery(self, learner_id, topic_id, status, confidence=None, notes=""):
        """Update mastery status."""
        return self.profile_mgr.update_mastery(learner_id, topic_id, status, confidence, notes)
    
    def get_profile(self, learner_id):
        """Get learner profile."""
        return self.profile_mgr.load_profile(learner_id)
    
    def create_plan(self, learner_id, **kwargs):
        """Create personalized learning plan."""
        return self.plan_gen.create_plan(learner_id, **kwargs)
    
    def generate_report(self, learner_id, mastered_ids, in_progress_ids=None):
        """Generate progress report."""
        return self.cluster_summarizer.generate_progress_report(learner_id, mastered_ids, in_progress_ids)
    
    # === Higher-Value Skills (9-12) ===
    def align_to_standards(self, topic_ids):
        """Align topics to curriculum standards."""
        return self.standards_aligner.align_path_to_standards(topic_ids)
    
    def portfolio_report(self, learner_id, mastered_ids, in_progress_ids=None):
        """Generate standards-aligned portfolio report."""
        return self.standards_aligner.generate_portfolio_report(learner_id, mastered_ids, in_progress_ids)
    
    def estimate_difficulty(self, topic_id, learner_age=None):
        """Estimate topic difficulty score."""
        return self.difficulty_est.estimate_difficulty(topic_id, learner_age)
    
    def estimate_path_difficulty(self, path_topic_ids, learner_age=None):
        """Estimate difficulty of a learning path."""
        return self.difficulty_est.estimate_path_difficulty(path_topic_ids, learner_age)
    
    def prepare_content(self, topic_id, content_type, **kwargs):
        """Prepare content generation prompts."""
        return self.content_router.route_request(topic_id, content_type, **kwargs)
    
    def log_diagnostic(self, learner_id, topic_id, format_type, score, passed):
        """Log diagnostic result for analysis."""
        return self.reflection.log_diagnostic_result(learner_id, topic_id, format_type, score, passed)
    
    def analyze_learner(self, learner_id):
        """Analyze learner patterns."""
        return self.reflection.analyze_learner_patterns(learner_id)
    
    def system_analysis(self):
        """Analyze system-wide patterns."""
        return self.reflection.analyze_system_patterns()
    
    def suggest_improvements(self):
        """Suggest skill improvements."""
        return self.reflection.suggest_skill_improvements()

if __name__ == "__main__":
    mg = MasteryGraphCore()
    
    print("=" * 60)
    print("MasteryGraph Core — Master Orchestrator")
    print("=" * 60)
    print(f"\nAll 12 skills loaded:")
    print(f"  ✅ Taxonomy Index (1,590 topics, 3,221 dependencies)")
    print(f"  ✅ compute_learning_path")
    print(f"  ✅ analyze_gaps")
    print(f"  ✅ generate_diagnostic")
    print(f"  ✅ generate_grounded_explanation")
    print(f"  ✅ update_learner_profile")
    print(f"  ✅ create_personalized_plan")
    print(f"  ✅ cluster_summary")
    print(f"  ✅ standards_alignment")
    print(f"  ✅ difficulty_estimator")
    print(f"  ✅ content_request_router")
    print(f"  ✅ self_reflection")
    
    # Quick demo
    print(f"\n🧪 Quick Demo:")
    results = mg.search_topics("fractions")
    if results:
        t = results[0]
        print(f"  Search 'fractions': found {len(results)} topics")
        print(f"  Top result: {t['name']} ({t['id']})")
        
        # Get explanation
        expl = mg.explain(t["id"], age=7)
        print(f"  Prerequisites: {len(expl['directPrerequisites'])} direct")
        
        # Difficulty
        diff = mg.estimate_difficulty(t["id"], 7)
        print(f"  Difficulty: {diff['difficultyScore']}/10 — {diff['interpretation']}")
        
        # Content prompt
        content = mg.prepare_content(t["id"], "visual", format="illustration", age=7)
        print(f"  Content prompt ready: {content['format']} ({len(content['prompt'])} chars)")
        
        print(f"\n  Ready to accept learner profiles and tasks.")
