---
name: masterygraph-difficulty
description: Estimate difficulty and time requirements for any topic or learning path. Factors in prerequisite depth, topic type, and age appropriateness. Use when setting realistic expectations or scheduling.
---

# MasteryGraph Difficulty Estimator

Estimates time and cognitive load for topics and paths.

## When to Use
- Set realistic expectations for a parent
- Estimate how long a unit will take
- Schedule a learning plan with appropriate pacing
- Identify topics that may need extra support

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from difficulty_estimator import DifficultyEstimator

est = DifficultyEstimator()
result = est.estimate(
    topic_ids=["topic_123", "topic_456"],
    learner_age=7,
    mastered_ids=["topic_001"]
)
```

## Returns
```json
{
  "estimates": [
    {
      "topic": {"id": "topic_123", "name": "Fractions"},
      "difficulty": "medium",
      "estimatedMinutes": 180,
      "prerequisiteDepth": 3,
      "confidence": 0.85
    }
  ],
  "totalEstimatedTime": "6 hours",
  "suggestedPacing": "2 weeks at 30 min/day"
}
```

## Parameters
- `topic_ids`: Topics to estimate (required)
- `learner_age`: Child's age (optional)
- `mastered_ids`: Already mastered topics (optional)
