---
name: masterygraph-gaps
description: Analyze prerequisite gaps for a target topic or goal. Given a learner's current mastery, returns the minimal set of unmastered prerequisites prioritized by hardness and centrality. Use when identifying what a child is missing before learning something new.
---

# MasteryGraph Gap Analyzer

Finds the smallest set of topics a child needs to learn before reaching a target.

## When to Use
- Diagnose why a child is struggling with a topic
- Pre-assessment before starting a new unit
- Identify foundational gaps in a subject area
- Prioritize remediation efforts

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from analyze_gaps import GapAnalyzer

analyzer = GapAnalyzer()
result = analyzer.analyze_gaps(
    target_topic_ids=["topic_123"],
    mastered_ids=["topic_001", "topic_002"],
    in_progress_ids=["topic_003"]
)
```

## Returns
```json
{
  "gaps": [
    {"id": "topic_004", "name": "Number Recognition", "priority": 1, "strength": "hard"}
  ],
  "alreadyMastered": [...],
  "inProgress": [...],
  "metadata": {
    "targetCount": 1,
    "totalGaps": 3,
    "criticalGaps": 2
  }
}
```

## Parameters
- `target_topic_ids`: Topics the learner wants to reach (required)
- `mastered_ids`: Already mastered topics (optional)
- `in_progress_ids`: Topics being worked on (optional)
