---
name: masterygraph-diagnostics
description: Generate age-appropriate diagnostic questions for any topic in the Marble Skill Taxonomy. Uses the topic's assessmentPrompts and evidence fields to create targeted questions. Use when assessing a child's readiness or mastery level.
---

# MasteryGraph Diagnostic Generator

Generates targeted diagnostic questions from the taxonomy's built-in assessment prompts.

## When to Use
- Assess a child's readiness for a new topic
- Evaluate mastery after completing a learning path
- Create pre/post assessments for a unit
- Identify specific misconceptions

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from generate_diagnostic import DiagnosticGenerator

gen = DiagnosticGenerator()
result = gen.generate_diagnostic(
    topic_id="topic_123",
    age=8,
    format="multiple_choice",  # or "open_ended", "mixed"
    count=5
)
```

## Returns
```json
{
  "topic": {"id": "topic_123", "name": "Addition within 10"},
  "questions": [
    {
      "type": "multiple_choice",
      "question": "What is 3 + 4?",
      "options": ["6", "7", "8", "9"],
      "correct": "7",
      "prerequisite": "Counting to 10"
    }
  ],
  "metadata": {
    "ageRange": "5-7",
    "subject": "Mathematics",
    "difficulty": "beginner"
  }
}
```

## Parameters
- `topic_id`: Topic to generate questions for (required)
- `age`: Child's age to filter appropriateness (optional)
- `format`: `multiple_choice`, `open_ended`, or `mixed` (default: mixed)
- `count`: Number of questions (default: 5)
