---
name: masterygraph-content
description: Route content requests to appropriate generation tools based on topic type, age, and purpose. Decides whether to generate a diagnostic, explanation, plan, or activity. Use when a parent asks for "help with math" or similar broad requests.
---

# MasteryGraph Content Router

Routes ambiguous requests to the right tool automatically.

## When to Use
- Parent says "my child needs help with fractions"
- Request is vague: "what should we do today?"
- Need to decide between diagnostic, explanation, or activity
- Multiple skills could apply — this picks the best one

## How to Use

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from content_request_router import ContentRouter

router = ContentRouter()
result = router.route(
    request="my child is struggling with fractions",
    learner_id="child_001",
    context="homework_help"
)
```

## Returns
```json
{
  "intent": "diagnose_and_explain",
  "actions": [
    {"skill": "masterygraph-diagnostics", "topic": "topic_123", "reason": "Assess current mastery"},
    {"skill": "masterygraph-explanation", "topic": "topic_123", "reason": "Provide remediation explanation"}
  ],
  "confidence": 0.92
}
```

## Parameters
- `request`: Natural language request (required)
- `learner_id`: Child's profile ID (optional)
- `context`: `homework_help`, `curriculum_planning`, `assessment`, etc. (optional)
