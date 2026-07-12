---
name: masterygraph-summary
description: Generate parent-friendly progress reports by cluster/domain. Summarizes mastery across subject areas, identifies strengths, and highlights next focus areas. Use when a parent asks "how is my child doing?"
---

# MasteryGraph Cluster Summary

Generates human-readable progress reports organized by subject cluster.

## When to Use
- Parent asks for a progress update
- Create end-of-term report cards
- Identify subject strengths and weaknesses
- Compare progress across different domains

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from cluster_summary import ClusterSummarizer

summarizer = ClusterSummarizer()
report = summarizer.generate_summary(
    learner_id="child_001",
    detail_level="standard"  # or "brief", "detailed"
)
```

## Returns
```json
{
  "learner": {"name": "Alice", "age": 7},
  "overallProgress": "45%",
  "clusters": [
    {
      "name": "Number Sense",
      "mastery": "80%",
      "strengths": ["Counting", "One-to-one correspondence"],
      "gaps": ["Skip counting by 5s"]
    }
  ],
  "recommendations": [
    "Focus on skip counting this week"
  ]
}
```

## Parameters
- `learner_id`: Child's profile ID (required)
- `detail_level`: `brief`, `standard`, or `detailed` (default: standard)
