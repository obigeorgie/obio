---
name: masterygraph-plans
description: Create personalized weekly or daily learning plans from gap analysis + learner profile + goals. Respects age appropriateness, prerequisite ordering, and time constraints. Use when a parent asks for a schedule or curriculum plan.
---

# MasteryGraph Plan Creator

Generates actionable weekly/daily plans from identified gaps and learner goals.

## When to Use
- Parent asks for a weekly learning schedule
- Create a daily activity plan for a child
- Build a curriculum plan for a homeschool term
- Adapt a plan based on updated mastery status

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from create_personalized_plan import PlanCreator

creator = PlanCreator()
plan = creator.create_plan(
    learner_id="child_001",
    goals=["topic_123", "topic_456"],
    duration_days=7,
    sessions_per_day=2,
    session_minutes=30
)
```

## Returns
```json
{
  "plan": {
    "duration": "7 days",
    "totalSessions": 14,
    "sessions": [
      {
        "day": 1,
        "session": 1,
        "topics": ["topic_001"],
        "activity": "Counting game with physical objects",
        "estimatedMinutes": 30
      }
    ]
  },
  "metadata": {
    "learnerAge": 7,
    "subjectFocus": "Mathematics",
    "prerequisiteCount": 3
  }
}
```

## Parameters
- `learner_id`: Child's profile ID (required)
- `goals`: Target topic IDs (required)
- `duration_days`: Plan length in days (default: 7)
- `sessions_per_day`: Sessions per day (default: 2)
- `session_minutes`: Minutes per session (default: 30)
