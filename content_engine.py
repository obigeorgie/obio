"""SEO Content Engine for MasteryGraph.
Auto-generates educational blog posts from the Marble taxonomy.
Drives organic traffic for 'how to teach [topic] to [age] year old' keywords."""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

CONTENT_DIR = Path(os.getenv("CONTENT_DIR", "/root/.openclaw/workspace/content"))
CONTENT_DIR.mkdir(exist_ok=True)

class ContentEngine:
    """Generates SEO-optimized educational content from taxonomy topics."""
    
    def __init__(self, taxonomy_path: str = None):
        self.taxonomy = self._load_taxonomy(taxonomy_path)
    
    def _load_taxonomy(self, path: str = None) -> List[Dict]:
        if path is None:
            path = "/root/.openclaw/workspace/marble-taxonomy/data/topics.json"
        try:
            with open(path) as f:
                data = json.load(f)
                return data.get("topics", [])
        except:
            return []
    
    def generate_blog_post(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """Generate a complete SEO blog post for a topic."""
        topic = None
        for t in self.taxonomy:
            if t.get("id") == topic_id:
                topic = t
                break
        
        if not topic:
            return None
        
        # Get prerequisites
        prereqs = []
        for dep_id in topic.get("prerequisites", []):
            for t in self.taxonomy:
                if t.get("id") == dep_id:
                    prereqs.append(t)
                    break
        
        age_start = topic.get("ageRangeStart", 5)
        age_end = topic.get("ageRangeEnd", 11)
        
        post = {
            "slug": self._slugify(topic.get("name", "")),
            "title": self._generate_title(topic, age_start, age_end),
            "meta_description": self._generate_meta_description(topic, age_start, age_end),
            "keywords": self._generate_keywords(topic),
            "content": self._generate_content(topic, prereqs, age_start, age_end),
            "prerequisites_section": self._generate_prerequisites_section(prereqs),
            "activities_section": self._generate_activities_section(topic, age_start),
            "assessment_cta": self._generate_assessment_cta(topic),
            "topic_id": topic_id,
            "subject": topic.get("subject", ""),
            "domain": topic.get("domain", ""),
            "age_range": f"{age_start}-{age_end}",
            "generated_at": datetime.now().isoformat(),
        }
        
        # Save to file
        filepath = CONTENT_DIR / f"{post['slug']}.md"
        with open(filepath, "w") as f:
            f.write(self._render_markdown(post))
        
        return post
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL slug."""
        return text.lower().replace(" ", "-").replace("/", "-").replace("&", "and")[:60]
    
    def _generate_title(self, topic: Dict, age_start: int, age_end: int) -> str:
        """Generate SEO-optimized title."""
        name = topic.get("name", "")
        templates = [
            f"How to Teach {name} to {age_start}-{age_end} Year Olds: A Complete Guide",
            f"{name} for Kids: Prerequisites, Activities & Teaching Tips (Ages {age_start}-{age_end})",
            f"The Parent's Guide to {name}: What Your {age_start}-{age_end} Year Old Needs to Know",
            f"Teaching {name}: Step-by-Step for {age_start}-{age_end} Year Olds",
        ]
        return templates[0]  # Use first template
    
    def _generate_meta_description(self, topic: Dict, age_start: int, age_end: int) -> str:
        """Generate meta description."""
        desc = topic.get("description", "")
        return (
            f"Learn how to teach {topic.get('name', '')} to {age_start}-{age_end} year olds. "
            f"Discover prerequisites, fun activities, and assessment tools. {desc[:100]}"
        )
    
    def _generate_keywords(self, topic: Dict) -> List[str]:
        """Generate SEO keywords."""
        name = topic.get("name", "")
        subject = topic.get("subject", "")
        return [
            f"how to teach {name.lower()} to kids",
            f"{name.lower()} for {topic.get('ageRangeStart', 5)} year olds",
            f"{subject.lower()} prerequisites",
            f"teaching {name.lower()} at home",
            f"{name.lower()} activities for kids",
            "mastery-based learning",
            "prerequisite skills",
        ]
    
    def _generate_content(self, topic: Dict, prereqs: List[Dict], age_start: int, age_end: int) -> str:
        """Generate main blog content."""
        name = topic.get("name", "")
        desc = topic.get("description", "")
        subject = topic.get("subject", "")
        
        content = f"""# {name}: A Complete Guide for Parents of {age_start}-{age_end} Year Olds

## What is {name}?

{desc}

Understanding {name} is a crucial milestone in your child's {subject.lower()} education. This skill builds the foundation for more advanced concepts and helps develop critical thinking abilities.

## Why Prerequisites Matter

Before diving into {name}, it's essential that your child has mastered the foundational skills. Our research-backed prerequisite chain ensures your child learns efficiently without frustration.

{self._generate_prerequisites_section(prereqs)}

## How to Know If Your Child Is Ready

Your child is likely ready for {name} if they can:
{self._generate_readiness_checks(topic, prereqs)}

## Fun Activities to Practice at Home

{self._generate_activities_section(topic, age_start)}

## Common Mistakes to Avoid

1. **Skipping prerequisites** — Children who jump ahead without mastering foundations often develop learning gaps
2. **Rushing the process** — Mastery takes time. Allow 2-3 weeks per prerequisite topic
3. **Using only worksheets** — Hands-on activities and real-world applications are more effective
4. **Forgetting to celebrate** — Small wins build confidence and motivation

## Assessing Your Child's Readiness

Want to know exactly where your child stands? Our free learning readiness assessment analyzes your child's age, current skills, and {name} prerequisites to create a personalized learning path.

{self._generate_assessment_cta(topic)}

## Related Topics

{self._generate_related_topics(topic)}

---

*This guide is powered by the Marble Skill Taxonomy — 1,590 research-backed topics with 3,221 prerequisite relationships, designed to help every child learn at their own pace.*
"""
        return content
    
    def _generate_prerequisites_section(self, prereqs: List[Dict]) -> str:
        """Generate prerequisite section."""
        if not prereqs:
            return "No specific prerequisites required! This is a great starting topic."
        
        lines = ["### Prerequisite Skills\n"]
        for i, prereq in enumerate(prereqs[:8], 1):
            lines.append(f"{i}. **{prereq.get('name', '')}** — {prereq.get('description', '')[:120]}")
        
        if len(prereqs) > 8:
            lines.append(f"\n*...and {len(prereqs) - 8} more foundational skills")
        
        return "\n".join(lines)
    
    def _generate_readiness_checks(self, topic: Dict, prereqs: List[Dict]) -> str:
        """Generate readiness checklist."""
        checks = []
        for prereq in prereqs[:5]:
            checks.append(f"- {self._readiness_check_for_topic(prereq)}")
        if not checks:
            checks.append(f"- Show interest in {topic.get('subject', 'learning')} activities")
        return "\n".join(checks)
    
    def _readiness_check_for_topic(self, topic: Dict) -> str:
        """Generate a readiness check for a topic."""
        name = topic.get("name", "").lower()
        if "count" in name:
            return "Count objects up to 20 without mistakes"
        elif "add" in name or "sum" in name:
            return "Add single-digit numbers mentally"
        elif "subtract" in name:
            return "Understand that subtraction means 'taking away'"
        elif "multiply" in name:
            return "Skip count by 2s, 5s, and 10s"
        elif "divide" in name:
            return "Share items equally among groups"
        elif "fraction" in name:
            return "Recognize halves and quarters in shapes"
        elif "read" in name or "comprehen" in name:
            return "Read simple sentences fluently"
        elif "write" in name:
            return "Write their name and simple words"
        else:
            return f"Demonstrate basic understanding of {topic.get('name', 'this topic')}"
    
    def _generate_activities_section(self, topic: Dict, age: int) -> str:
        """Generate activity ideas."""
        subject = topic.get("subject", "").lower()
        name = topic.get("name", "").lower()
        
        activities = []
        
        if "math" in subject or "add" in name or "subtract" in name:
            activities = [
                "**Grocery Store Math**: Give your child $5 in play money. Have them 'buy' items and calculate change.",
                "**Number Scavenger Hunt**: Find numbers in your neighborhood (house numbers, license plates, store signs).",
                "**Cooking Together**: Double a recipe together. If you need 2 cups of flour, how much for double?",
                "**Story Problems**: Create silly word problems. 'If you have 7 dinosaurs and I eat 3, how many are left?'",
            ]
        elif "read" in name or "language" in subject:
            activities = [
                "**Picture Walk**: Before reading, look at pictures and predict the story together.",
                "**Character Voices**: Read dialogue using different voices for each character.",
                "**Story Retelling**: After reading, have your child retell the story in their own words.",
                "**Word Hunt**: Find sight words in books, on signs, and in recipes.",
            ]
        elif "science" in subject:
            activities = [
                "**Nature Journal**: Observe and draw plants, insects, or weather patterns daily.",
                "**Kitchen Science**: Mix baking soda and vinegar. What happens? Why?",
                "**Shadow Tracing**: Trace shadows at different times of day. Why do they change?",
                "**Sink or Float**: Test household objects in water. Predict first, then test!",
            ]
        else:
            activities = [
                f"**Real-World Connections**: Point out {topic.get('name', 'this skill')} in everyday life.",
                "**Hands-On Exploration**: Use household items to explore the concept physically.",
                "**Teach-Back Method**: Have your child explain the concept to a stuffed animal.",
                "**Game-Based Learning**: Turn practice into a game with points and rewards.",
            ]
        
        return "\n\n".join(activities)
    
    def _generate_assessment_cta(self, topic: Dict) -> str:
        """Generate assessment call-to-action."""
        return f"""
<div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 2rem; border-radius: 16px; color: white; text-align: center; margin: 2rem 0;">
  <h3 style="margin: 0 0 1rem; font-size: 1.5rem;">🎯 Get Your Free Learning Readiness Assessment</h3>
  <p style="margin: 0 0 1.5rem; opacity: 0.9;">
    See exactly which prerequisite skills your child has mastered and which ones to focus on next.
  </p>
  <a href="https://app.obiomacare.com/assessment?topic={self._slugify(topic.get('name', ''))}" 
     style="display: inline-block; background: white; color: #6366f1; padding: 0.875rem 2rem; border-radius: 10px; text-decoration: none; font-weight: 700;">
    Start Free Assessment →
  </a>
</div>
"""
    
    def _generate_related_topics(self, topic: Dict) -> str:
        """Generate related topics links."""
        subject = topic.get("subject", "")
        related = []
        for t in self.taxonomy:
            if t.get("subject") == subject and t.get("id") != topic.get("id"):
                related.append(t)
                if len(related) >= 5:
                    break
        
        if not related:
            return ""
        
        lines = []
        for t in related:
            lines.append(f"- [{t.get('name', '')}](https://app.obiomacare.com/assessment?topic={self._slugify(t.get('name', ''))})")
        
        return "\n".join(lines)
    
    def _render_markdown(self, post: Dict) -> str:
        """Render post as markdown."""
        return f"""---
title: "{post['title']}"
description: "{post['meta_description']}"
keywords: {', '.join(post['keywords'])}
subject: {post['subject']}
domain: {post['domain']}
age_range: {post['age_range']}
generated_at: {post['generated_at']}
---

{post['content']}
"""
    
    def generate_batch(self, count: int = 10, subject_filter: Optional[str] = None) -> List[Dict]:
        """Generate a batch of blog posts."""
        posts = []
        topics = self.taxonomy
        
        if subject_filter:
            topics = [t for t in topics if t.get("subject") == subject_filter]
        
        # Sort by popularity (topics with more prerequisites = more fundamental)
        topics = sorted(topics, key=lambda t: len(t.get("prerequisites", [])), reverse=True)
        
        for topic in topics[:count]:
            post = self.generate_blog_post(topic.get("id"))
            if post:
                posts.append(post)
        
        return posts
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get content generation stats."""
        files = list(CONTENT_DIR.glob("*.md"))
        posts = []
        for f in files:
            with open(f) as fh:
                content = fh.read()
                # Extract title
                title = ""
                for line in content.split("\n"):
                    if line.startswith("title:"):
                        title = line.split('"')[1] if '"' in line else line.split(":", 1)[1].strip()
                        break
                posts.append({"slug": f.stem, "title": title})
        
        return {
            "total_posts": len(files),
            "posts": posts,
            "content_dir": str(CONTENT_DIR),
        }

_engine = None

def get_content_engine() -> ContentEngine:
    global _engine
    if _engine is None:
        _engine = ContentEngine()
    return _engine
