"""Partnership Outreach System for OBIO.
Manages outreach to homeschool networks, tutoring centers, and schools."""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

OUTREACH_DIR = Path(os.getenv("OUTREACH_DIR", "/root/.openclaw/workspace/outreach"))
OUTREACH_DIR.mkdir(exist_ok=True)
CONTACTS_FILE = OUTREACH_DIR / "contacts.json"
TEMPLATES_FILE = OUTREACH_DIR / "templates.json"

class OutreachManager:
    """Manages partnership outreach campaigns."""
    
    def __init__(self):
        self.contacts = self._load_contacts()
        self.templates = self._load_templates()
    
    def _load_contacts(self) -> Dict:
        if CONTACTS_FILE.exists():
            with open(CONTACTS_FILE) as f:
                return json.load(f)
        return {}
    
    def _save_contacts(self):
        with open(CONTACTS_FILE, "w") as f:
            json.dump(self.contacts, f, indent=2)
    
    def _load_templates(self) -> Dict:
        if TEMPLATES_FILE.exists():
            with open(TEMPLATES_FILE) as f:
                return json.load(f)
        
        # Default templates
        templates = {
            "homeschool_coop": {
                "subject": "Free Learning Path Tool for {coop_name} Families",
                "body": """Hi {contact_name},

I'm reaching out because I know {coop_name} is dedicated to helping families provide the best education for their children.

I built OBIO — a free tool that generates personalized learning paths based on 1,590 research-backed topics and prerequisite chains. It answers the question every homeschooling parent asks: "What should my child learn next?"

**What it does:**
- Enter any topic + child's age → get a complete prerequisite path
- See exactly which skills to master before tackling harder topics
- Track progress with mastery badges
- AI tutor explains any concept in age-appropriate language

**For co-ops like yours:**
- Free unlimited assessments for all families
- 20% commission on any paid subscriptions (Family Plan: $12/mo)
- White-label reports with your co-op branding
- Bulk learner management for tutors

I'd love to offer {coop_name} families free access. Would you be open to a 10-minute call this week?

Best,
Nnamdi
Founder, OBIO
https://app.obiomacare.com

P.S. Try the free assessment tool: https://app.obiomacare.com/assessment
""",
            },
            "tutoring_center": {
                "subject": "Cut Your Lesson Prep Time in Half — OBIO for Tutors",
                "body": """Hi {contact_name},

Running a tutoring center means juggling lesson plans for dozens of students with different needs and skill levels.

I built OBIO to solve exactly that. It maps 1,590 topics with 3,221 prerequisite relationships — so you instantly know what each student needs to learn next.

**For tutoring centers:**
- Generate prerequisite paths in seconds (not hours)
- Identify learning gaps before they become problems
- Track mastery across all your students
- AI tutor handles basic questions, freeing you for complex instruction
- Educator Plan: $29/mo for up to 20 learners

**Partnership offer:**
- 30% commission on referrals
- Co-branded assessment reports
- Priority API access

Can we schedule a 15-minute demo this week?

Best,
Nnamdi
Founder, OBIO
https://app.obiomacare.com
""",
            },
            "school": {
                "subject": "Data-Driven Differentiation for {school_name}",
                "body": """Hi {contact_name},

Differentiated instruction is powerful but time-consuming. Teachers at {school_name} are likely spending hours each week trying to figure out where each student stands and what they need next.

OBIO automates that process using a research-backed prerequisite taxonomy (1,590 topics, 3,221 dependencies). It's like having a curriculum specialist for every student.

**For schools:**
- Instant gap analysis for any learning objective
- Prerequisite chains aligned to standards
- Progress dashboards for teachers and admin
- Early warning system for at-risk students
- School Plan: $299/year unlimited

**Pilot program:**
We're offering 10 schools a 30-day free pilot with full support. No commitment, no credit card.

Would {school_name} be interested in joining the pilot?

Best,
Nnamdi
Founder, OBIO
https://app.obiomacare.com
""",
            },
            "influencer": {
                "subject": "Partnership: Help Parents Teach Smarter (20% Commission)",
                "body": """Hi {contact_name},

I follow your content on {platform} and love how you make {topic} accessible for parents.

I built OBIO — a tool that maps exactly what kids need to learn before tackling any topic. It uses 1,590 research-backed skills with prerequisite chains (like a GPS for learning).

**Why your audience will love it:**
- Free learning readiness assessments
- Personalized learning paths for any topic
- AI tutor for instant help
- No more guessing what comes next

**Partnership terms:**
- 20% recurring commission on all referrals
- Custom discount code for your followers
- Co-branded assessment landing page
- Monthly performance reports

Interested in trying it? I'll set up a custom link for you.

Best,
Nnamdi
Founder, OBIO
https://app.obiomacare.com
""",
            },
        }
        
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(templates, f, indent=2)
        
        return templates
    
    def add_contact(self, contact_type: str, name: str, email: str, 
                   organization: str = "", notes: str = "", 
                   platform: str = "", website: str = "") -> Dict:
        """Add a new outreach contact."""
        contact_id = f"{contact_type}_{os.urandom(4).hex()}"
        contact = {
            "id": contact_id,
            "type": contact_type,
            "name": name,
            "email": email,
            "organization": organization,
            "notes": notes,
            "platform": platform,
            "website": website,
            "status": "new",
            "added_at": datetime.now().isoformat(),
            "last_contact": None,
            "emails_sent": [],
            "responses": [],
        }
        
        self.contacts[contact_id] = contact
        self._save_contacts()
        return contact
    
    def generate_outreach_email(self, contact_id: str, template_name: str = None) -> Optional[Dict]:
        """Generate an outreach email for a contact."""
        contact = self.contacts.get(contact_id)
        if not contact:
            return None
        
        # Auto-select template based on contact type
        if not template_name:
            template_map = {
                "homeschool_coop": "homeschool_coop",
                "tutoring_center": "tutoring_center",
                "school": "school",
                "influencer": "influencer",
            }
            template_name = template_map.get(contact["type"], "homeschool_coop")
        
        template = self.templates.get(template_name)
        if not template:
            return None
        
        # Render template
        context = {
            "contact_name": contact["name"].split()[0] if contact["name"] else "there",
            "coop_name": contact["organization"] or "your co-op",
            "school_name": contact["organization"] or "your school",
            "platform": contact.get("platform", "social media"),
            "topic": contact.get("notes", "education"),
        }
        
        subject = template["subject"]
        body = template["body"]
        
        for key, value in context.items():
            subject = subject.replace(f"{{{key}}}", str(value))
            body = body.replace(f"{{{key}}}", str(value))
        
        return {
            "contact_id": contact_id,
            "to": contact["email"],
            "subject": subject,
            "body": body,
            "template": template_name,
        }
    
    def mark_contacted(self, contact_id: str, email_id: str = None, response: str = None):
        """Mark a contact as contacted."""
        if contact_id in self.contacts:
            self.contacts[contact_id]["last_contact"] = datetime.now().isoformat()
            if email_id:
                self.contacts[contact_id]["emails_sent"].append({
                    "email_id": email_id,
                    "sent_at": datetime.now().isoformat(),
                })
            if response:
                self.contacts[contact_id]["responses"].append({
                    "response": response,
                    "received_at": datetime.now().isoformat(),
                })
            self.contacts[contact_id]["status"] = "contacted"
            self._save_contacts()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get outreach statistics."""
        total = len(self.contacts)
        by_type = {}
        by_status = {}
        
        for contact in self.contacts.values():
            ct = contact["type"]
            cs = contact["status"]
            by_type[ct] = by_type.get(ct, 0) + 1
            by_status[cs] = by_status.get(cs, 0) + 1
        
        return {
            "total_contacts": total,
            "by_type": by_type,
            "by_status": by_status,
            "templates_available": list(self.templates.keys()),
        }
    
    def export_csv(self) -> str:
        """Export contacts as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "type", "name", "email", "organization", "status", "added_at", "last_contact"])
        
        for contact in self.contacts.values():
            writer.writerow([
                contact["id"],
                contact["type"],
                contact["name"],
                contact["email"],
                contact["organization"],
                contact["status"],
                contact["added_at"],
                contact["last_contact"] or "",
            ])
        
        return output.getvalue()

_manager = None

def get_outreach_manager() -> OutreachManager:
    global _manager
    if _manager is None:
        _manager = OutreachManager()
    return _manager
