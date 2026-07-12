#!/usr/bin/env python3
"""
MasteryGraph Core — Skill 4: generate_diagnostic
Using assessmentPrompt and evidence fields, create age-appropriate 
diagnostic questions or tasks for a specific micro-topic or cluster.
"""

import json
from pathlib import Path

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class DiagnosticGenerator:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.topic_by_name = load_index("topic_by_name")
    
    def generate_diagnostic(self, topic_id, format="auto", age=None, num_questions=3):
        """
        Generate a diagnostic for a specific topic.
        
        Args:
            topic_id: The micro-topic ID to diagnose
            format: "quiz", "observation", "self-report", or "auto" (picks based on topic type)
            age: Child's age (for tone adjustment)
            num_questions: Number of questions/tasks to generate
        
        Returns:
            Dict with diagnostic content, format, and scoring guidance
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        # Determine best format
        if format == "auto":
            topic_type = topic.get("type", "CONCEPTUAL")
            if topic_type == "PROCEDURAL":
                format = "quiz"
            elif topic_type == "META":
                format = "self-report"
            else:
                format = "observation"
        
        age = age or topic.get("ageRangeStart", 6)
        assessment_prompt = topic.get("assessmentPrompt", "")
        evidence_criteria = topic.get("evidence", [])
        
        # Build diagnostic
        diagnostic = {
            "topicId": topic_id,
            "topicName": topic.get("name"),
            "subject": topic.get("subject"),
            "domain": topic.get("domain"),
            "targetAge": age,
            "format": format,
            "assessmentPrompt": assessment_prompt,
        }
        
        if format == "quiz":
            diagnostic["questions"] = self._build_quiz_questions(topic, age, num_questions, evidence_criteria)
        elif format == "observation":
            diagnostic["tasks"] = self._build_observation_tasks(topic, age, num_questions, evidence_criteria)
        elif format == "self-report":
            diagnostic["prompts"] = self._build_self_report(topic, age, num_questions)
        
        diagnostic["scoringGuide"] = self._build_scoring_guide(evidence_criteria, format)
        diagnostic["nextSteps"] = self._suggest_next_steps(topic)
        
        return diagnostic
    
    def _build_quiz_questions(self, topic, age, num, evidence_criteria):
        """Build procedural quiz questions."""
        questions = []
        
        # Use assessment prompt as basis
        prompt = topic.get("assessmentPrompt", f"Demonstrate understanding of {topic['name']}")
        
        for i in range(num):
            q = {
                "id": f"q{i+1}",
                "type": "procedural",
                "question": f"Question {i+1}: {prompt}",
                "difficulty": "basic" if i == 0 else ("intermediate" if i == 1 else "advanced"),
                "evidenceTarget": evidence_criteria[i] if i < len(evidence_criteria) else "Correct application",
            }
            questions.append(q)
        
        return questions
    
    def _build_observation_tasks(self, topic, age, num, evidence_criteria):
        """Build observation-based tasks for conceptual topics."""
        tasks = []
        prompt = topic.get("assessmentPrompt", f"Show understanding of {topic['name']}")
        
        for i in range(num):
            task = {
                "id": f"task{i+1}",
                "type": "observation",
                "setup": f"Set up a scenario where the child encounters {topic['name']}.",
                "watchFor": evidence_criteria[i] if i < len(evidence_criteria) else prompt,
                "prompt": f"Ask: '{prompt}'" if prompt else f"Present a situation involving {topic['name']}.",
                "difficulty": "basic" if i == 0 else ("intermediate" if i == 1 else "advanced"),
            }
            tasks.append(task)
        
        return tasks
    
    def _build_self_report(self, topic, age, num):
        """Build self-report prompts for meta/soft skills."""
        name = topic.get("name", "this skill")
        prompts = [
            {
                "id": f"sr1",
                "type": "self-report",
                "prompt": f"When you face a difficult problem with {name}, what do you usually do first?",
                "options": ["Give up", "Ask for help immediately", "Try on my own first", "Break it into smaller parts"],
            },
            {
                "id": f"sr2",
                "type": "self-report",
                "prompt": f"How confident do you feel about {name}?",
                "options": ["Not confident", "A little confident", "Quite confident", "Very confident"],
            },
            {
                "id": f"sr3",
                "type": "self-report",
                "prompt": f"Tell me about a time you used {name} successfully.",
                "options": [],  # Open response
            },
        ]
        return prompts[:num]
    
    def _build_scoring_guide(self, evidence_criteria, format):
        """Build scoring guidance."""
        if format == "quiz":
            return {
                "mastered": f"Correctly answers {len(evidence_criteria)} out of {len(evidence_criteria)} evidence criteria",
                "inProgress": "Some correct with prompting",
                "notStarted": "Unable to complete without significant help",
            }
        elif format == "observation":
            return {
                "mastered": "Demonstrates criteria spontaneously in natural context",
                "inProgress": "Demonstrates with prompting or in structured context",
                "notStarted": "Does not demonstrate even with support",
            }
        else:
            return {
                "mastered": "Self-reports confidence and provides concrete examples",
                "inProgress": "Acknowledges skill but cannot provide examples",
                "notStarted": "Does not recognize the skill in themselves",
            }
    
    def _suggest_next_steps(self, topic):
        """Suggest what to do based on diagnostic results."""
        return [
            "If mastered: Move to next topic in learning path",
            "If in progress: Continue practice with varied contexts",
            "If not started: Review prerequisites and try again",
        ]
    
    def generate_cluster_diagnostic(self, cluster_id, age=None):
        """Generate a broader diagnostic for a cluster of topics."""
        # This would need cluster-topic mapping which isn't directly in the JSON
        # For now, placeholder
        return {"error": "Cluster diagnostics require cluster-topic mapping"}

if __name__ == "__main__":
    gen = DiagnosticGenerator()
    
    print("=" * 60)
    print("Skill 4: generate_diagnostic")
    print("=" * 60)
    
    # Demo: Diagnostic for fractions
    results = [t for t in gen.topic_by_id.values() if "fractions" in t["name"].lower()]
    if results:
        target = results[0]
        print(f"\nTopic: {target['name']} ({target['id']})")
        print(f"Assessment prompt: {target.get('assessmentPrompt', 'N/A')[:100]}...")
        print(f"Evidence criteria: {len(target.get('evidence', []))} items")
        
        diag = gen.generate_diagnostic(target["id"], age=7)
        
        print(f"\nFormat: {diag['format']}")
        print(f"Target age: {diag['targetAge']}")
        
        if "questions" in diag:
            print(f"\nQuestions ({len(diag['questions'])}):")
            for q in diag["questions"]:
                print(f"  [{q['difficulty']}] {q['question'][:80]}...")
        
        print(f"\nScoring guide:")
        for level, desc in diag["scoringGuide"].items():
            print(f"  {level}: {desc}")
