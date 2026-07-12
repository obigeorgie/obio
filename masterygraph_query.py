#!/usr/bin/env python3
"""
MasteryGraph Core — Query Tool
Quick lookups by ID, name, subject, domain, or age.
"""

import json
from pathlib import Path

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class TaxonomyQuery:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
        self.topic_by_name = load_index("topic_by_name")
        self.topics_by_subject = load_index("topics_by_subject")
        self.topics_by_domain = load_index("topics_by_domain")
        self.topics_by_type = load_index("topics_by_type")
        self.prereqs_for = load_index("dependencies_by_topic")
        self.needed_by = load_index("needed_by_prereq")
        self.clusters = load_index("clusters")
    
    def get_topic(self, topic_id):
        """Get topic by ID."""
        return self.topic_by_id.get(topic_id)
    
    def get_topic_by_name(self, name):
        """Get topic by exact name."""
        return self.topic_by_name.get(name)
    
    def search_topics(self, query):
        """Simple substring search across topic names."""
        query = query.lower()
        return [t for t in self.topic_by_id.values() if query in t["name"].lower()]
    
    def get_prerequisites(self, topic_id):
        """Get all prerequisites for a topic."""
        deps = self.prereqs_for.get(topic_id, [])
        result = []
        for d in deps:
            prereq = self.topic_by_id.get(d["prerequisiteId"])
            if prereq:
                result.append({
                    "dependency": d,
                    "topic": prereq
                })
        return result
    
    def get_dependents(self, topic_id):
        """Get all topics that depend on this one."""
        deps = self.needed_by.get(topic_id, [])
        result = []
        for d in deps:
            topic = self.topic_by_id.get(d["topicId"])
            if topic:
                result.append({
                    "dependency": d,
                    "topic": topic
                })
        return result
    
    def get_topics_by_subject(self, subject):
        return self.topics_by_subject.get(subject, [])
    
    def get_topics_by_domain(self, domain):
        return self.topics_by_domain.get(domain, [])
    
    def get_topics_by_type(self, typ):
        return self.topics_by_type.get(typ, [])

if __name__ == "__main__":
    q = TaxonomyQuery()
    
    # Demo: lookup a few topics by ID
    print("=" * 60)
    print("MasteryGraph Core — Query Validation")
    print("=" * 60)
    
    # Get a math topic
    math_topics = q.get_topics_by_subject("Mathematics")
    if math_topics:
        t = math_topics[0]
        print(f"\n[Sample Lookup by ID]")
        print(f"  ID: {t['id']}")
        print(f"  Name: {t['name']}")
        print(f"  Subject: {t.get('subject')}")
        print(f"  Domain: {t.get('domain')}")
        print(f"  Type: {t.get('type')}")
        print(f"  Age: {t.get('ageRangeStart')}-{t.get('ageRangeEnd')}")
        
        # Query by ID
        looked_up = q.get_topic(t['id'])
        print(f"\n  Lookup by ID '{t['id']}': {'✅ FOUND' if looked_up else '❌ NOT FOUND'}")
        
        # Prerequisites
        prereqs = q.get_prerequisites(t['id'])
        print(f"  Prerequisites: {len(prereqs)}")
        
        # Dependents
        dependents = q.get_dependents(t['id'])
        print(f"  Topics that depend on this: {len(dependents)}")
    
    # Search demo
    print(f"\n[Search Demo: 'fractions']")
    results = q.search_topics("fractions")
    print(f"  Found {len(results)} topics matching 'fractions'")
    for r in results[:5]:
        print(f"    - {r['name']} ({r['id']}) [{r.get('subject')}]")
    
    print(f"\n✅ Query system ready. {len(q.topic_by_id)} topics indexed.")
