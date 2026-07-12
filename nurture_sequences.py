"""Email Nurture Sequences for MasteryGraph Growth.
Automated email sequences that convert free users to paid subscribers."""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from email_service import email_service

class NurtureSequence:
    """Manages email nurture sequences for user conversion."""
    
    # Sequence definitions: (day, subject, template, condition)
    ASSESSMENT_SEQUENCE = [
        {
            "day": 0,
            "subject": "Your child's learning assessment is ready!",
            "template": "assessment_complete",
            "condition": "assessment_completed",
        },
        {
            "day": 1,
            "subject": "The #1 mistake parents make when teaching math",
            "template": "educational_tip_1",
            "condition": "not_signed_up",
        },
        {
            "day": 3,
            "subject": "How prerequisite skills unlock your child's potential",
            "template": "educational_tip_2",
            "condition": "not_signed_up",
        },
        {
            "day": 5,
            "subject": "Case study: From struggling to thriving in 6 weeks",
            "template": "case_study",
            "condition": "not_signed_up",
        },
        {
            "day": 7,
            "subject": "🎁 7-day free trial of MasteryGraph Family",
            "template": "trial_offer",
            "condition": "not_signed_up",
        },
        {
            "day": 10,
            "subject": "What teachers don't tell you about learning gaps",
            "template": "educational_tip_3",
            "condition": "not_signed_up",
        },
        {
            "day": 14,
            "subject": "Last chance: Your free trial expires today",
            "template": "trial_ending",
            "condition": "not_signed_up",
        },
    ]
    
    TRIAL_SEQUENCE = [
        {
            "day": 0,
            "subject": "Welcome to MasteryGraph! Let's get started",
            "template": "trial_welcome",
            "condition": "trial_started",
        },
        {
            "day": 1,
            "subject": "Day 1: Add your first learner profile",
            "template": "trial_day_1",
            "condition": "no_learners_added",
        },
        {
            "day": 3,
            "subject": "Day 3: Try the gap analysis tool",
            "template": "trial_day_3",
            "condition": "no_gap_analysis",
        },
        {
            "day": 5,
            "subject": "Day 5: Generate a personalized learning plan",
            "template": "trial_day_5",
            "condition": "no_plan_generated",
        },
        {
            "day": 7,
            "subject": "Your trial is ending — here's what you'll lose",
            "template": "trial_ending_reminder",
            "condition": "not_subscribed",
        },
        {
            "day": 10,
            "subject": "We miss you! Come back for 50% off",
            "template": "win_back",
            "condition": "not_subscribed",
        },
    ]
    
    PAID_SEQUENCE = [
        {
            "day": 0,
            "subject": "Welcome to MasteryGraph Family! 🎉",
            "template": "paid_welcome",
            "condition": "subscription_active",
        },
        {
            "day": 7,
            "subject": "Your first week progress report",
            "template": "weekly_progress",
            "condition": "subscription_active",
        },
        {
            "day": 30,
            "subject": "Your monthly mastery report",
            "template": "monthly_report",
            "condition": "subscription_active",
        },
    ]
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load email templates."""
        templates = {
            "assessment_complete": """
Hi {parent_name},

Great news! I've analyzed {child_name}'s readiness for {topic_name}.

**Readiness Level: {readiness_level}**
{readiness_explanation}

**Learning Path:**
{learning_path}

**Get the full experience with MasteryGraph Family:**
- Personalized learning plans for every topic
- Progress tracking with mastery badges
- AI tutor for instant explanations
- Weekly progress reports
- Unlimited learners

[Start Your Free Trial →](https://app.obiomacare.com/register?assessment={assessment_id})

Questions? Just reply to this email.

— MasteryGraph Team
""",
            "educational_tip_1": """
Hi {parent_name},

The biggest mistake I see parents make?

Jumping to advanced topics before their child has mastered the prerequisites.

It's like trying to build a house starting from the second floor. The foundation matters.

Here's what works:
1. Identify the prerequisites (we do this automatically)
2. Master each one before moving on
3. Use real-world examples (not just worksheets)
4. Celebrate small wins (mastery badges work wonders)

{child_name}'s assessment showed {readiness_level} for {topic_name}. The prerequisite path I generated is the safest route to success.

[See the full path →](https://app.obiomacare.com/assessment/{assessment_id})

— MasteryGraph Team
""",
            "educational_tip_2": """
Hi {parent_name},

Prerequisites aren't just "review." They're the neural pathways that make advanced learning possible.

When a child learns addition before multiplication, they're not just memorizing facts. They're building a cognitive framework that makes multiplication intuitive.

That's why skipping prerequisites creates learning gaps that show up years later.

{child_name}'s assessment identified {prereq_count} prerequisite topics for {topic_name}. Each one is a stepping stone, not an obstacle.

[See the prerequisite ladder →](https://app.obiomacare.com/assessment/{assessment_id})

— MasteryGraph Team
""",
            "case_study": """
Hi {parent_name},

Meet Sarah, mother of 7-year-old Marcus.

Marcus was struggling with 2-digit addition. His teacher said he was "behind."

But the real problem? He hadn't fully mastered single-digit addition — the prerequisite.

We generated a 3-week prerequisite plan. Single-digit addition → place value understanding → 2-digit addition.

6 weeks later, Marcus was not just caught up. He was ahead.

The key: prerequisites, not pressure.

{child_name} has a similar path waiting. The assessment already identified the exact steps.

[Get the full plan →](https://app.obiomacare.com/register?assessment={assessment_id})

— MasteryGraph Team
""",
            "trial_offer": """
Hi {parent_name},

You've seen the assessment. Now see the full power of MasteryGraph.

**7-day free trial includes:**
✅ Unlimited learning plans for every topic
✅ AI tutor for instant explanations
✅ Progress tracking with mastery badges
✅ Weekly email reports
✅ Gap analysis for any learning goal
✅ Up to 3 learners (Family Plan)

No credit card required. Cancel anytime.

[Start Free Trial →](https://app.obiomacare.com/register?assessment={assessment_id}&trial=true)

If it's not the best learning tool you've ever used, you pay nothing.

— MasteryGraph Team
""",
            "trial_welcome": """
Hi {parent_name},

Welcome to MasteryGraph Family! 🎉

Your 7-day trial is active. Let's make the most of it.

**Day 1 Action:** Add your first learner profile
[Add Learner →](https://app.obiomacare.com/learners)

**Day 2 Action:** Search for a topic they want to learn
[Search Topics →](https://app.obiomacare.com/search)

**Day 3 Action:** Run a gap analysis
[Gap Analysis →](https://app.obiomacare.com/gap-analysis)

Need help? Reply to this email or check the [Quick Start Guide](https://app.obiomacare.com/docs).

— MasteryGraph Team
""",
            "trial_ending_reminder": """
Hi {parent_name},

Your 7-day free trial ends in 24 hours.

If you don't subscribe, you'll lose:
- All personalized learning plans
- Progress tracking and mastery badges
- AI tutor access
- Weekly progress reports
- All learner data

**Keep everything for just $12/month:**
[Subscribe Now →](https://app.obiomacare.com/pricing)

Questions? Just reply.

— MasteryGraph Team
""",
            "paid_welcome": """
Hi {parent_name},

Welcome to MasteryGraph Family! You're now part of a community of parents who refuse to let their children fall through the cracks of standardized education.

**What happens next:**
1. I'll send you a weekly progress report every Sunday
2. You'll get mastery notifications when {child_name} levels up
3. AI tutor is available 24/7 for any questions

**Your subscription:**
Plan: Family Plan
Amount: $12/month
Renewal: {renewal_date}

Questions? Just reply to this email.

— MasteryGraph Team
""",
            "weekly_progress": """
Hi {parent_name},

Here's {child_name}'s progress this week:

{progress_summary}

Keep going! Small, consistent steps lead to mastery.

[View Full Dashboard →](https://app.obiomacare.com/dashboard)

— MasteryGraph Team
""",
        }
        return templates
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render an email template with context variables."""
        template = self.templates.get(template_name, "")
        for key, value in context.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template
    
    def send_sequence_email(self, user_email: str, sequence_type: str, 
                           day: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send a specific email from a nurture sequence."""
        sequences = {
            "assessment": self.ASSESSMENT_SEQUENCE,
            "trial": self.TRIAL_SEQUENCE,
            "paid": self.PAID_SEQUENCE,
        }
        
        sequence = sequences.get(sequence_type, [])
        step = next((s for s in sequence if s["day"] == day), None)
        
        if not step:
            return {"sent": False, "error": f"No email for day {day} in {sequence_type} sequence"}
        
        body = self.render_template(step["template"], context)
        
        result = email_service._send(
            to=user_email,
            subject=step["subject"],
            html=body.replace("\n", "<br>"),
            text=body,
        )
        
        return {
            "sent": result.get("success", False),
            "email_id": result.get("id"),
            "sequence": sequence_type,
            "day": day,
            "subject": step["subject"],
        }
    
    def get_next_emails(self, user_email: str, sequence_type: str, 
                       start_date: datetime, current_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of emails that should be sent next for a user."""
        sequences = {
            "assessment": self.ASSESSMENT_SEQUENCE,
            "trial": self.TRIAL_SEQUENCE,
            "paid": self.PAID_SEQUENCE,
        }
        
        sequence = sequences.get(sequence_type, [])
        days_elapsed = (datetime.now() - start_date).days
        
        next_emails = []
        for step in sequence:
            if step["day"] <= days_elapsed:
                # Check if condition is met
                condition = step["condition"]
                should_send = self._check_condition(condition, current_status)
                if should_send:
                    next_emails.append(step)
        
        return next_emails
    
    def _check_condition(self, condition: str, status: Dict[str, Any]) -> bool:
        """Check if a condition is met for sending an email."""
        if condition == "assessment_completed":
            return True  # Always send after assessment
        elif condition == "not_signed_up":
            return not status.get("has_account", False)
        elif condition == "trial_started":
            return status.get("trial_active", False)
        elif condition == "no_learners_added":
            return status.get("learner_count", 0) == 0
        elif condition == "no_gap_analysis":
            return not status.get("has_run_gap_analysis", False)
        elif condition == "no_plan_generated":
            return not status.get("has_generated_plan", False)
        elif condition == "not_subscribed":
            return not status.get("subscription_active", False)
        elif condition == "subscription_active":
            return status.get("subscription_active", False)
        return True

_nurture = None

def get_nurture() -> NurtureSequence:
    global _nurture
    if _nurture is None:
        _nurture = NurtureSequence()
    return _nurture
