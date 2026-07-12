#!/usr/bin/env python3
"""
MasteryGraph Core — Taxonomy Loader & Indexer
Loads, validates, and indexes the Marble Skill Taxonomy for fast queries.
"""

import json
from collections import defaultdict
from pathlib import Path

TAXONOMY_DIR = Path("/root/.openclaw/workspace/marble-taxonomy")
DATA_DIR = TAXONOMY_DIR / "data"
INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_json(filename):
    """Load a JSON file from the data directory."""
    path = DATA_DIR / filename
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_index():
    """Load taxonomy files, validate counts, build indexes."""
    print("=" * 60)
    print("MasteryGraph Core — Taxonomy Loader")
    print("=" * 60)
    
    # 1. Load manifest
    print("\n[1/6] Loading manifest...")
    manifest = load_json("manifest.json")
    print(f"  Taxonomy version: {manifest['taxonomyVersion']}")
    print(f"  Generated at: {manifest['generatedAt']}")
    
    # 2. Load topics
    print("\n[2/6] Loading topics.json...")
    topics_data = load_json("topics.json")
    topics = topics_data if isinstance(topics_data, list) else topics_data.get("topics", [])
    print(f"  Topics loaded: {len(topics)}")
    
    # 3. Load dependencies
    print("\n[3/6] Loading dependencies.json...")
    deps_data = load_json("dependencies.json")
    dependencies = deps_data if isinstance(deps_data, list) else deps_data.get("dependencies", [])
    print(f"  Dependencies loaded: {len(dependencies)}")
    
    # 4. Load clusters
    print("\n[4/6] Loading clusters.json...")
    clusters_data = load_json("clusters.json")
    if isinstance(clusters_data, dict):
        clusters = clusters_data.get("clusters", [])
    else:
        clusters = clusters_data if isinstance(clusters_data, list) else []
    print(f"  Clusters loaded: {len(clusters)}")
    
    # 5. Load curriculum standards
    print("\n[5/6] Loading curriculum-standards.json...")
    standards_data = load_json("curriculum-standards.json")
    if isinstance(standards_data, dict):
        curricula = standards_data.get("curricula", [])
        standards_flat = []
        for curr in curricula:
            for std in curr.get("standards", []):
                std["_curriculum"] = curr.get("name", "unknown")
                std["_source"] = curr.get("source", "unknown")
                standards_flat.append(std)
    else:
        curricula = []
        standards_flat = []
    print(f"  Curricula: {len(curricula)}")
    print(f"  Standards loaded: {len(standards_flat)}")
    
    # 6. Validate counts
    print("\n[6/6] Validating counts against manifest...")
    expected = manifest["counts"]
    
    validations = [
        ("topics", len(topics), expected["topics"]),
        ("dependencies", len(dependencies), expected["dependencies"]),
        ("clusters", len(clusters), expected["clusters"]),
    ]
    
    all_pass = True
    for name, actual, exp in validations:
        status = "✅ PASS" if actual == exp else "❌ FAIL"
        if actual != exp:
            all_pass = False
        print(f"  {name}: {actual} / {exp} {status}")
    
    if all_pass:
        print("\n🎉 All validations passed!")
    else:
        print("\n⚠️ Some validations failed!")
    
    # 7. Build indexes
    print("\n[7/7] Building indexes...")
    INDEX_DIR.mkdir(exist_ok=True)
    
    # Topic by ID
    topic_by_id = {t["id"]: t for t in topics}
    # Topic by name
    topic_by_name = {t["name"]: t for t in topics}
    # Topics by subject
    topics_by_subject = defaultdict(list)
    # Topics by domain
    topics_by_domain = defaultdict(list)
    # Topics by age range
    topics_by_age = defaultdict(list)
    # Topics by type
    topics_by_type = defaultdict(list)
    
    for t in topics:
        topics_by_subject[t.get("subject", "Unknown")].append(t)
        topics_by_domain[t.get("domain", "Unknown")].append(t)
        topics_by_type[t.get("type", "Unknown")].append(t)
        age_start = t.get("ageRangeStart", 0)
        age_end = t.get("ageRangeEnd", 18)
        age_key = f"{age_start}-{age_end}"
        topics_by_age[age_key].append(t)
    
    # Dependency indexes
    # Forward: topic -> what it depends on (prerequisites)
    prereqs_for = defaultdict(list)
    # Reverse: prereq -> topics that need it
    needed_by = defaultdict(list)
    
    for d in dependencies:
        tid = d["topicId"]
        pid = d["prerequisiteId"]
        prereqs_for[tid].append(d)
        needed_by[pid].append(d)
    
    # Save indexes as JSON
    with open(INDEX_DIR / "topic_by_id.json", "w", encoding="utf-8") as f:
        json.dump(topic_by_id, f, indent=2)
    
    with open(INDEX_DIR / "topic_by_name.json", "w", encoding="utf-8") as f:
        json.dump(topic_by_name, f, indent=2)
    
    with open(INDEX_DIR / "topics_by_subject.json", "w", encoding="utf-8") as f:
        json.dump(dict(topics_by_subject), f, indent=2)
    
    with open(INDEX_DIR / "topics_by_domain.json", "w", encoding="utf-8") as f:
        json.dump(dict(topics_by_domain), f, indent=2)
    
    with open(INDEX_DIR / "topics_by_type.json", "w", encoding="utf-8") as f:
        json.dump(dict(topics_by_type), f, indent=2)
    
    with open(INDEX_DIR / "dependencies_by_topic.json", "w", encoding="utf-8") as f:
        json.dump(dict(prereqs_for), f, indent=2)
    
    with open(INDEX_DIR / "needed_by_prereq.json", "w", encoding="utf-8") as f:
        json.dump(dict(needed_by), f, indent=2)
    
    with open(INDEX_DIR / "clusters.json", "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2)
    
    with open(INDEX_DIR / "curricula.json", "w", encoding="utf-8") as f:
        json.dump(curricula, f, indent=2)
    
    # Stats
    print(f"\n📊 Index Stats:")
    print(f"  Topics by subject:")
    for subj, ts in sorted(topics_by_subject.items(), key=lambda x: -len(x[1])):
        print(f"    {subj}: {len(ts)}")
    print(f"\n  Topic types:")
    for typ, ts in sorted(topics_by_type.items(), key=lambda x: -len(x[1])):
        print(f"    {typ}: {len(ts)}")
    print(f"\n  Hard dependencies: {sum(1 for d in dependencies if d.get('strength') == 'hard')}")
    print(f"  Soft dependencies: {sum(1 for d in dependencies if d.get('strength') == 'soft')}")
    print(f"  Topics with prerequisites: {len(prereqs_for)}")
    print(f"  Topics that are prerequisites for others: {len(needed_by)}")
    
    print(f"\n💾 Indexes saved to: {INDEX_DIR}")
    print(f"  Files: topic_by_id.json, topic_by_name.json, topics_by_subject.json,")
    print(f"         topics_by_domain.json, topics_by_type.json,")
    print(f"         dependencies_by_topic.json, needed_by_prereq.json,")
    print(f"         clusters.json, curricula.json")
    
    return {
        "topic_by_id": topic_by_id,
        "topic_by_name": topic_by_name,
        "topics_by_subject": dict(topics_by_subject),
        "topics_by_domain": dict(topics_by_domain),
        "topics_by_type": dict(topics_by_type),
        "prereqs_for": dict(prereqs_for),
        "needed_by": dict(needed_by),
        "clusters": clusters,
        "curricula": curricula,
        "manifest": manifest,
    }

if __name__ == "__main__":
    indexes = build_index()
