"""AI Tutor module for MasteryGraph.
Provides intelligent tutoring via LLM API (OpenRouter compatible)."""
import os
import requests
from typing import Optional, Dict, Any, List

# OpenRouter configuration
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct")

class AITutor:
    """AI tutor powered by LLM for personalized education."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or LLM_API_KEY
        self.base_url = base_url or LLM_API_BASE
        self.model = model or LLM_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        if not self.api_key:
            return "AI tutor is not configured. Please set LLM_API_KEY or OPENROUTER_API_KEY environment variable."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Add OpenRouter-specific headers if using OpenRouter
        if "openrouter" in self.base_url.lower():
            headers["HTTP-Referer"] = "https://app.obiomacare.com"
            headers["X-Title"] = "MasteryGraph"
        
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"AI tutor error: {resp.status_code} - {resp.text[:200]}"
        except Exception as e:
            return f"AI tutor error: {str(e)}"

    def explain_topic(self, topic_name: str, topic_description: str, age: int, prerequisite_topics: List[str] = None) -> str:
        """Generate an age-appropriate explanation of a topic."""
        prereq_text = ""
        if prerequisite_topics:
            prereq_text = f"\nPrerequisites the student should know: {', '.join(prerequisite_topics)}"

        messages = [
            {"role": "system", "content": "You are a warm, encouraging tutor for children. Explain concepts in simple, concrete terms with examples. Use analogies and storytelling. Keep explanations concise but complete."},
            {"role": "user", "content": f"Explain this topic to a {age}-year-old child in a warm, encouraging way.\n\nTopic: {topic_name}\nDescription: {topic_description}{prereq_text}\n\nMake it engaging with real-world examples and analogies."}
        ]
        return self._chat(messages, temperature=0.7, max_tokens=1500)

    def generate_practice_problems(self, topic_name: str, age: int, difficulty: str = "medium", count: int = 3) -> str:
        """Generate practice problems for a topic."""
        messages = [
            {"role": "system", "content": "You are a tutor creating practice problems for children. Create clear, engaging problems with step-by-step solutions. Include hints."},
            {"role": "user", "content": f"Generate {count} {difficulty} practice problems for a {age}-year-old about: {topic_name}\n\nFor each problem:\n1. Present the problem clearly\n2. Provide the answer\n3. Include a hint\n\nFormat with markdown."}
        ]
        return self._chat(messages, temperature=0.8, max_tokens=2000)

    def answer_question(self, question: str, age: int, topic_context: str = "") -> str:
        """Answer a student's question with context."""
        context = f"\nContext: {topic_context}" if topic_context else ""
        messages = [
            {"role": "system", "content": "You are a patient, encouraging tutor for children. Answer questions simply and accurately. If you don't know something, say so honestly."},
            {"role": "user", "content": f"A {age}-year-old student asks: {question}{context}\n\nPlease answer in a warm, encouraging way suitable for their age."}
        ]
        return self._chat(messages, temperature=0.7, max_tokens=1500)

    def provide_hint(self, topic_name: str, problem: str, age: int, attempt_history: str = "") -> str:
        """Provide a hint without giving away the answer."""
        history = f"\nStudent's previous attempts: {attempt_history}" if attempt_history else ""
        messages = [
            {"role": "system", "content": "You are a tutor who provides helpful hints. Never give the full answer. Guide the student to discover it themselves. Use the Socratic method."},
            {"role": "user", "content": f"Topic: {topic_name}\nProblem: {problem}{history}\n\nProvide a helpful hint for a {age}-year-old. Don't give the answer - guide them to figure it out."}
        ]
        return self._chat(messages, temperature=0.6, max_tokens=800)

    def generate_learning_path_summary(self, topic_path: List[str], age: int) -> str:
        """Generate a motivating summary of a learning path."""
        path_str = " → ".join(topic_path)
        messages = [
            {"role": "system", "content": "You are an encouraging tutor. Motivate students to learn by showing them the exciting journey ahead."},
            {"role": "user", "content": f"A {age}-year-old student is about to learn these topics in order: {path_str}\n\nWrite a short, encouraging summary that makes them excited to learn. Highlight what cool things they'll be able to do after each step. Keep it under 200 words."}
        ]
        return self._chat(messages, temperature=0.8, max_tokens=600)

    def assess_understanding(self, topic_name: str, age: int, student_answer: str, correct_answer: str) -> Dict[str, Any]:
        """Assess a student's understanding from their answer."""
        messages = [
            {"role": "system", "content": "You are a tutor assessing a student's work. Provide constructive feedback. Identify what they got right and what needs improvement. Be encouraging."},
            {"role": "user", "content": f"Topic: {topic_name}\nStudent's answer: {student_answer}\nCorrect answer: {correct_answer}\n\nProvide a brief assessment in JSON format with: understanding (poor/fair/good/excellent), feedback (encouraging string), and suggestions (array of 1-2 specific tips)."}
        ]
        response = self._chat(messages, temperature=0.5, max_tokens=800)
        # Try to parse JSON, fallback to text
        try:
            import json
            return json.loads(response)
        except:
            return {
                "understanding": "unknown",
                "feedback": response,
                "suggestions": ["Review the topic and try again"]
            }

_tutor = None

def get_tutor() -> AITutor:
    global _tutor
    if _tutor is None:
        _tutor = AITutor()
    return _tutor
