---
name: masterygraph-standards
description: Map Marble Skill Taxonomy topics to curriculum standards (CCSS, NGSS, IB, etc.). Generate alignment reports for schools, homeschool parents, or portfolio documentation. Use when demonstrating standards compliance.
---

# MasteryGraph Standards Aligner

Maps topics to 7 indexed curricula for compliance and documentation.

## When to Use
- Homeschool parent needs standards documentation
- School needs curriculum alignment report
- Portfolio documentation for compliance review
- Compare Marble topics to state/national standards

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from standards_alignment import StandardsAligner

aligner = StandardsAligner()
report = aligner.align_topics(
    topic_ids=["topic_123", "topic_456"],
    curricula=["CCSS", "NGSS"]  # or all if omitted
)
```

## Returns
```json
{
  "alignments": [
    {
      "topic": {"id": "topic_123", "name": "Addition within 10"},
      "standards": [
        {"code": "K.OA.A.2", "title": "Solve addition word problems", "curriculum": "CCSS"}
      ]
    }
  ],
  "coverage": {
    "CCSS": "85%",
    "NGSS": "60%"
  }
}
```

## Parameters
- `topic_ids`: Topics to align (required)
- `curricula`: Specific curricula to check (optional, defaults to all)
