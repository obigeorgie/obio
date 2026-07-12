---
name: masterygraph-paths
description: Compute a personalized learning path through the Marble Skill Taxonomy. Given target topics and current mastery state, returns a topological sequence respecting hard/soft prerequisites. Use when generating a learning plan or route for a child.
---

# MasteryGraph Learning Path Computer

Computes a minimal valid learning path from a child's current state to target topics.

## When to Use
- Parent asks "what should my child learn next?"
- Need to generate a progression from A to B
- Want to see the prerequisite chain for a topic
- Building a weekly/daily learning plan

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from compute_learning_path import LearningPathEngine

engine = LearningPathEngine()
result = engine.compute_path(
    target_topic_ids=["topic_123", "topic_456"],
    mastered_ids=["topic_001", "topic_002"],
    age=8,
    max_topics=50
)
```

## Returns
```json
{
  "path": [
    {"id": "topic_003", "name": "Counting to 10", "reason": "prerequisite for Addition"},
    ...
  ],
  "metadata": {
    "totalTopics": 5,
    "hardDependencies": 4,
    "softDependencies": 1,
    "estimatedTime": "2 weeks"
  }
}
```

## Parameters
- `target_topic_ids`: List of topic IDs to reach (required)
- `mastered_ids`: Topics already known (optional, default [])
- `age`: Child's age to filter age-appropriate topics (optional)
- `max_topics`: Hard limit on path length (default 50)
