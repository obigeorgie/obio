# Banger Post Generator — Rosie | NurseEvolutionCoach

Generate X (Twitter), LinkedIn, TikTok, Instagram, and YouTube content optimized for the Grok-Phoenix recommendation algorithm.

## When to Use

- Creating new social media posts for @CEORosie_bot
- Refreshing existing content calendar
- Testing new content archetypes
- Building viral-style posts for nursing entrepreneurship niche

## Parameters

- `topic`: The nursing entrepreneurship topic (e.g., "burnout recovery", "pricing services", "legal structures")
- `platform`: Target platform (x, linkedin, tiktok, instagram, youtube)
- `archetype`: Optional — force a specific archetype (contrarian_take, direct_question, micro_story, you_vs_them, state_specific_intel, hot_take)
- `tone`: empathetic | direct | provocative | educational (default: empathetic)
- `include_video`: true | false (default: false)

## Output Format

```
ARCHETYPE: [type]
PLATFORM: [platform]
HOOK TYPE: [hook style]
PREDICTED TOP SIGNAL: [replies/reposts/bookmarks/profile_visits]

MAIN POST:
[Optimized content following Phoenix rules]

FIRST REPLY (X only, if link/CTA needed):
[Reply content with link]

REPLY STRATEGY (First 30 minutes):
- [How to handle comment type A]
- [How to handle comment type B]

MEDIA NOTES:
[Video/image description if applicable]
```

## Phoenix Algorithm Rules (From xai-org/x-algorithm)

### Top Signals to Optimize
1. **REPLIES** — Highest weight (27×). Spark genuine conversation. Open questions.
2. **BOOKMARKS** — Strong signal (24×). Save-worthy content. Checklists, frameworks, stats.
3. **PROFILE VISITS** — Deep engagement (15×). "Who wrote this?"
4. **REPOSTS/QUOTES** — Strong signal. Content worth sharing.
5. **DWELL TIME** — Video content, threads, high-value text.
6. **LIKES** — Lowest weight (0.5×). Nice but don't optimize for likes alone.

### Negative Signals to Avoid
- Blocks/Mutes — hurt 10× more than likes help (algorithm heavily penalizes)
- External links in MAIN POST (X) — suppresses reach dramatically
- Hashtags on X — interpreted as broadcast spam, reduces distribution
- Duplicate/low-quality content
- Rage-bait — triggers defensive blocks from nurses
- Inconsistent posting schedule

### Velocity Rules
- First 30-60 minutes determines distribution
- Reply to EVERY comment in first 30 minutes
- Consistent daily posting builds positive history signals

## Platform Rules

### X (Twitter)
- **NO hashtags. Use natural keywords instead.** Phoenix algorithm interprets hashtags as broadcast signals and downweights reach.
- NO external links in main post. Ever. Reply with link.
- Optimal: 180-280 characters for singles
- Threads: Each tweet standalone-able, first = pure hook
- Video strongly preferred (30-60 sec)
- Best times: 7-9 AM, 7-9 PM ET (shift change)

### LinkedIn
- Longer form, bullet points, professional tone
- Links OK in main post
- Career pivot stories, frameworks, legal compliance
- CTA: "Comment below if you're navigating this"

### TikTok
- 30-60 sec video, direct to camera
- First 3 seconds = stakes
- Pattern: Problem → Pivot → Proof → CTA
- Text overlay boosts watch time

### Instagram
- Carousel posts for educational content
- 5-7 slides, each standalone insight
- Explicit "Save this" CTA works

### YouTube
- 8-15 min educational
- First 30 sec = result promise
- Timestamped chapters boost retention

## Archetypes

### 1. Contrarian Take
Challenge nursing orthodoxy constructively. End with "Agree or disagree?" / "Change my mind."

### 2. Micro-Story + Open Loop
Personal moment with stakes. "Thread 🧵" or "Continue reading 👇"

### 3. Direct Question
Specific, personal, easy answer. "I'll go first." / "Drop yours below."

### 4. "You vs. Them" Reframe
Power dynamic reversal. "Save this for your next shift."

### 5. State-Specific Intel
Time-sensitive rules. "Tag a [STATE] nurse who needs this."

### 6. Hot Take
Provocative statement nurses feel strongly about. "Change my mind."

## Examples

See `banger_post_generator.md` for full examples and templates.

## Integration

Use with:
- `schedule_posts_phoenix.py` — automated Postiz scheduling
- `engagement-monitor/` — track which archetypes perform best
- Postiz CLI for multi-platform publishing

## Anti-Patterns

❌ Rage-bait about hospital admin  
❌ Pure venting without actionable pivot  
❌ External links in main X post  
❌ Inconsistent posting  
❌ Generic motivational quotes  
❌ "Link in bio" in main post
