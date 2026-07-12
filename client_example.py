#!/usr/bin/env python3
"""
MasteryGraph Core — Python Client Example

Shows how to call the MasteryGraph API from Python.
"""

import requests

BASE_URL = "http://localhost:8000"
API_KEY = "mg-live-2026"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

# ───────────────────────────────────────────────────────────────────────────
# Example 1: Search topics
# ───────────────────────────────────────────────────────────────────────────
print("=== Search Topics ===")
r = requests.get(f"{BASE_URL}/topics/search", params={"q": "fractions"}, headers=headers)
print(f"Found {r.json()['count']} topics")
for t in r.json()["results"][:3]:
    print(f"  - {t['name']} ({t['id']})")

# ───────────────────────────────────────────────────────────────────────────
# Example 2: Compute learning path
# ───────────────────────────────────────────────────────────────────────────
print("\n=== Compute Learning Path ===")
r = requests.post(
    f"{BASE_URL}/paths/compute",
    json={"target_topic_ids": ["mt_IHipFGTFEY"], "age": 7},
    headers=headers,
)
path = r.json()
print(f"Path to 'Understanding fractions': {path['stats']['totalSteps']} steps")
print(f"Hard dependencies: {path['stats']['hardDependencies']}")
print(f"First 3 topics: {[t['name'] for t in path['path'][:3]]}")

# ───────────────────────────────────────────────────────────────────────────
# Example 3: Create learner profile
# ───────────────────────────────────────────────────────────────────────────
print("\n=== Create Learner Profile ===")
r = requests.post(
    f"{BASE_URL}/learners",
    json={"learner_id": "client_demo_child", "name": "Amara", "age": 7, "grade": "2nd"},
    headers=headers,
)
print(f"Created: {r.json()['metadata']['name']}, age {r.json()['metadata']['age']}")

# ───────────────────────────────────────────────────────────────────────────
# Example 4: Estimate difficulty
# ───────────────────────────────────────────────────────────────────────────
print("\n=== Estimate Difficulty ===")
r = requests.post(
    f"{BASE_URL}/difficulty/estimate",
    json={"topic_id": "mt_IHipFGTFEY", "learner_age": 7},
    headers=headers,
)
diff = r.json()
print(f"Difficulty: {diff['difficultyScore']}/10 — {diff['interpretation']}")
print(f"Age appropriate: {diff['ageAppropriate']}")

# ───────────────────────────────────────────────────────────────────────────
# Example 5: Generate content prompt
# ───────────────────────────────────────────────────────────────────────────
print("\n=== Prepare Content ===")
r = requests.post(
    f"{BASE_URL}/content/prepare",
    json={"topic_id": "mt_IHipFGTFEY", "content_type": "visual", "format": "illustration", "age": 7},
    headers=headers,
)
content = r.json()
print(f"Format: {content['format']}")
print(f"Prompt: {content['prompt'][:120]}...")

print("\n✅ All examples completed successfully")
