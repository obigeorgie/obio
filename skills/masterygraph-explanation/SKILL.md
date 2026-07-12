---
name: masterygraph-explanation
description: Generate a grounded explanation for any topic, explicitly citing prerequisite chains. Uses the taxonomy's graph structure to explain WHY a topic is needed and what comes before/after. Use when explaining a concept to a parent or child.
---

# MasteryGraph Explanation Generator

Generates explanations with explicit prerequisite references — every claim is traceable to the graph.

## When to Use
- Explain why a topic is important to a parent
- Show a child what they need to learn first
- Create parent-friendly progress reports
- Document prerequisite chains for curriculum planning

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from generate_grounded_explanation import ExplanationGenerator

gen = ExplanationGenerator()
result = gen.explain(
    topic_id="topic_123",
    depth=3,  # how many levels of prereqs to include
    audience="parent"  # or "child", "teacher"
)
```

## Returns
```json
{
  "topic": {"id": "topic_123", "name": "Fractions"},
  "explanation": "Fractions build on division and equal parts...",
  "prerequisites": [
    {"id": "topic_100", "name": "Division", "relationship": "hard"},
    {"id": "topic_101", "name": "Equal Parts", "relationship": "soft"}
  ],
  "nextSteps": [
    {"id": "topic_200", "name": "Decimals"}
  ],
  "metadata": {"depth": 3, "audience": "parent"}
}
```

## Parameters
- `topic_id`: Topic to explain (required)
- `depth`: Levels of prerequisite chain to include (default: 3)
- `audience`: `parent`, `child`, or `teacher` (default: parent)
