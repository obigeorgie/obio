#!/bin/bash
# Bulk content generation script for MasteryGraph SEO engine
# Run this daily to generate fresh content from the taxonomy

API_KEY="mg_JIAmW4QTRqhncnQmkkQpX2TibuNEYm-jwY6wsz6Um3s"
API_BASE="https://api.obiomacare.com/v1"

SUBJECTS=("Mathematics" "Language Arts" "Science")
POSTS_PER_SUBJECT=5

echo "=== MasteryGraph Content Engine - Bulk Generation ==="
echo "Started: $(date)"
echo ""

for subject in "${SUBJECTS[@]}"; do
  echo "Generating $POSTS_PER_SUBJECT posts for: $subject"
  curl -s -X POST "${API_BASE}/content/generate?count=${POSTS_PER_SUBJECT}&subject=${subject// /+}" \
    -H "X-API-Key: ${API_KEY}"
  echo ""
  sleep 2
done

echo ""
echo "=== Content Stats ==="
curl -s "${API_BASE}/content/stats" | python3 -m json.tool

echo ""
echo "Completed: $(date)"
