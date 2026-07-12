#!/usr/bin/env python3
"""
MasteryGraph Core — Higher-Value Skill 3: Content Request Router
When rich visuals, storybooks, or videos are needed, prepare structured 
prompts for external multimodal tools (Higgsfield, image gen, etc.)
rather than generating low-quality content internally.
"""

import json
from pathlib import Path

INDEX_DIR = Path("/root/.openclaw/workspace/masterygraph-index")

def load_index(name):
    with open(INDEX_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

class ContentRouter:
    def __init__(self):
        self.topic_by_id = load_index("topic_by_id")
    
    def prepare_visual_prompt(self, topic_id, format="illustration", age=None, style="educational"):
        """
        Prepare a detailed prompt for an image/illustration generation tool.
        
        Args:
            topic_id: Topic to visualize
            format: "illustration", "diagram", "infographic", "storyboard"
            age: Target age for visual complexity
            style: "educational", "whimsical", "realistic", "minimal"
        
        Returns:
            Dict with ready-to-send prompt and metadata
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        age = age or topic.get("ageRangeStart", 6)
        name = topic.get("name", "")
        description = topic.get("description", "")
        subject = topic.get("subject", "")
        
        # Age-appropriate visual complexity
        complexity = {
            4: "simple, bold shapes, primary colors, minimal text",
            5: "clear imagery, friendly characters, some labels",
            6: "detailed but clear, labeled diagrams, engaging characters",
            7: "more detailed, some abstraction, clear labels",
            8: "complex diagrams, multiple elements, annotations",
            9: "sophisticated visuals, data representations, detailed labels",
            10: "advanced diagrams, real-world contexts, technical labels",
            11: "complex multi-step visuals, technical accuracy",
        }
        visual_complexity = complexity.get(min(11, max(4, age)), "clear and educational")
        
        prompts = {
            "illustration": f"Educational illustration for {age}-year-old children about '{name}'. "
                          f"{description[:150]}. Style: {style}, {visual_complexity}. "
                          f"Subject area: {subject}. No text in image except essential labels. "
                          f"Warm, encouraging tone. Diverse representation.",
            
            "diagram": f"Clear educational diagram showing '{name}' for {age}-year-olds. "
                      f"{description[:150]}. {visual_complexity}. "
                      f"Label key parts. Use arrows and visual cues. Clean layout.",
            
            "infographic": f"Simple infographic about '{name}' for children age {age}. "
                          f"Visual summary of: {description[:100]}. "
                          f"{visual_complexity}. Include 3-5 key visual elements. "
                          f"Icon-based where possible.",
            
            "storyboard": f"3-panel storyboard illustrating '{name}' for age {age}. "
                         f"Scene 1: Introduction/Setup. Scene 2: Action/Process. Scene 3: Result. "
                         f"{visual_complexity}. Consistent characters. No dialogue text.",
        }
        
        return {
            "topicId": topic_id,
            "topicName": name,
            "format": format,
            "targetAge": age,
            "prompt": prompts.get(format, prompts["illustration"]),
            "negativePrompt": "text-heavy, cluttered, scary, inappropriate, overly complex, blurry",
            "dimensions": "1024x1024" if format == "illustration" else "1024x768",
            "usage": "Educational content for mastery-based learning platform",
            "readyForTool": True,
        }
    
    def prepare_video_prompt(self, topic_id, duration=60, age=None, format="explainer"):
        """
        Prepare a structured prompt for video generation.
        
        Args:
            topic_id: Topic to explain
            duration: Target duration in seconds
            age: Target age
            format: "explainer", "story", "tutorial", "song"
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        age = age or topic.get("ageRangeStart", 6)
        name = topic.get("name", "")
        description = topic.get("description", "")
        
        # Scene breakdown based on duration
        scenes = max(2, duration // 15)  # ~15s per scene
        
        prompts = {
            "explainer": {
                "concept": f"Explain '{name}' to a {age}-year-old",
                "hook": f"Start with a relatable question about {name}",
                "explanation": f"Break down {description[:100]} into simple steps",
                "examples": f"Show 2 real-world examples a {age}-year-old would encounter",
                "closing": f"Quick recap and encouragement to practice",
            },
            "story": {
                "concept": f"Tell a story that teaches '{name}'",
                "characters": f"Age-appropriate protagonist ({age} years old)",
                "conflict": f"Character encounters a problem that requires {name}",
                "resolution": f"Character learns and applies {name} successfully",
                "moral": f"Learning {name} helps solve problems",
            },
            "tutorial": {
                "concept": f"Step-by-step tutorial for '{name}'",
                "steps": f"Break into {scenes} clear steps",
                "visuals": "Show hand/character performing each step",
                "tips": f"Common mistakes for {age}-year-olds and how to avoid",
                "practice": "End with a practice challenge",
            },
        }
        
        return {
            "topicId": topic_id,
            "topicName": name,
            "format": format,
            "targetAge": age,
            "targetDuration": duration,
            "sceneCount": scenes,
            "scriptOutline": prompts.get(format, prompts["explainer"]),
            "visualDirection": f"Age-appropriate visuals for {age}-year-olds. "
                              f"Clear, engaging, educational. "
                              f"Diverse representation. No scary or inappropriate content.",
            "audioDirection": f"Clear, warm narration. Pace appropriate for age {age}. "
                            f"Optional: gentle background music. No jarring sounds.",
            "readyForTool": True,
        }
    
    def prepare_storybook_prompt(self, topic_id, pages=8, age=None):
        """
        Prepare a storybook generation prompt.
        """
        topic = self.topic_by_id.get(topic_id)
        if not topic:
            return {"error": f"Topic {topic_id} not found"}
        
        age = age or topic.get("ageRangeStart", 6)
        name = topic.get("name", "")
        
        return {
            "topicId": topic_id,
            "topicName": name,
            "format": "storybook",
            "targetAge": age,
            "pages": pages,
            "storyOutline": {
                "page1": f"Introduction: Meet the character and setting related to {name}",
                "page2": f"Discovery: Character encounters {name} in their world",
                "page3-4": f"Learning: Character explores {name} with a friend/mentor",
                "page5-6": f"Challenge: Character faces a problem using {name}",
                "page7": f"Success: Character applies {name} to solve the problem",
                "page8": f"Closing: Celebration and invitation to explore more",
            },
            "visualStyle": f"Picture book style for age {age}. Warm colors, expressive characters. "
                          f"Each page has a full illustration with minimal text overlay.",
            "textStyle": f"Simple sentences, age-appropriate vocabulary (age {age}). "
                        f"Engaging, rhythmic where possible. Repetition for younger ages.",
            "readyForTool": True,
        }
    
    def route_request(self, topic_id, content_type, **kwargs):
        """
        Main routing function — route to appropriate content generator.
        
        Args:
            topic_id: Topic to create content for
            content_type: "visual", "video", "storybook", "interactive"
            **kwargs: Additional params (age, style, duration, etc.)
        """
        if content_type == "visual":
            return self.prepare_visual_prompt(topic_id, **kwargs)
        elif content_type == "video":
            return self.prepare_video_prompt(topic_id, **kwargs)
        elif content_type == "storybook":
            return self.prepare_storybook_prompt(topic_id, **kwargs)
        else:
            return {
                "error": f"Unknown content type: {content_type}",
                "supportedTypes": ["visual", "video", "storybook"],
            }

if __name__ == "__main__":
    router = ContentRouter()
    
    print("=" * 60)
    print("Higher-Value Skill 3: Content Request Router")
    print("=" * 60)
    
    # Demo: Route content requests
    results = [t for t in router.topic_by_id.values() if "fractions" in t["name"].lower()]
    if results:
        topic = results[0]
        tid = topic["id"]
        
        print(f"\n🎨 Visual Prompt (illustration):")
        visual = router.route_request(tid, "visual", format="illustration", age=7)
        print(f"  {visual['prompt'][:120]}...")
        
        print(f"\n🎬 Video Prompt (explainer):")
        video = router.route_request(tid, "video", format="explainer", duration=60, age=7)
        print(f"  Concept: {video['scriptOutline']['concept']}")
        print(f"  Scenes: {video['sceneCount']}")
        
        print(f"\n📖 Storybook Prompt:")
        book = router.route_request(tid, "storybook", pages=8, age=7)
        print(f"  Pages: {book['pages']}")
        print(f"  Page 1: {book['storyOutline']['page1']}")
        
        print(f"\n✅ All prompts ready for external multimodal tools")
