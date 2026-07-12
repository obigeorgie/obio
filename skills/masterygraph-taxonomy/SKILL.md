---
name: masterygraph-taxonomy
description: Load, validate, and index the Marble Skill Taxonomy for MasteryGraph. Returns topic counts, dependency counts, and validates graph integrity. Use when the agent needs to initialize or refresh the taxonomy data.
---

# MasteryGraph Taxonomy Loader

Loads and indexes the Marble Skill Taxonomy (1,590 topics, 3,221 dependencies) from GitHub.

## When to Use
- Agent needs to initialize the taxonomy
- Validate taxonomy integrity after updates
- Get statistics about topics, dependencies, and clusters
- Verify a specific topic exists in the graph

## How to Use

```python
from skills.taxonomy_loader import TaxonomyLoader
loader = TaxonomyLoader()
stats = loader.get_stats()
```

Or directly:
```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills")
from taxonomy_loader import TaxonomyLoader
loader = TaxonomyLoader()
stats = loader.get_stats()
```

## Returns
```json
{
  "totalTopics": 1590,
  "totalDependencies": 3221,
  "totalClusters": 183,
  "curricula": 7,
  "subjects": [...],
  "validation": {"errors": [], "warnings": []}
}
```

## Key Files
- `/root/.openclaw/workspace/masterygraph_loader.py` — Main loader script
- `/root/.openclaw/workspace/marble-taxonomy/` — Taxonomy data
- `/root/.openclaw/workspace/masterygraph-index/` — JSON indexes
