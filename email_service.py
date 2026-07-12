"""Email notification service using Resend API."""
import os
import requests
from typing import Optional, List

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM_EMAIL", "OBIO <admin@obiomacare.com>")

class EmailService:
    """Send transactional emails via Resend."""
    
    def __init__(self):
        self.api_key = RESEND_API_KEY
        self.from_email = RESEND_FROM
        self.base_url = "https://api.resend.com/emails"
    
    def _send(self, to: str, subject: str, html: str, text: Optional[str] = None) -> dict:
        if not self.api_key:
            return {"status": "skipped", "reason": "RESEND_API_KEY not configured"}
        
        payload = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if text:
            payload["text"] = text
        
        try:
            resp = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            if resp.status_code in (200, 202):
                return {"status": "sent", "id": resp.json().get("id")}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "detail": str(e)}
    
    def send_welcome(self, to: str, name: str) -> dict:
        html = f"""
        <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 40px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 28px;">🎯 Welcome to OBIO!</h1>
                <p style="margin: 16px 0 0; opacity: 0.9;">Every child learns in a network, not a line.</p>
            </div>
            <div style="padding: 40px; background: white;">
                <p style="font-size: 18px; color: #1a1a2e;">Hi {name or "there"},</p>
                <p style="color: #64748b; line-height: 1.6;">
                    Your OBIO account is ready. You now have access to 1,590+ micro-topics 
                    and 3,221 prerequisite relationships to help your child learn exactly what they need, 
                    in the right order.
                </p>
                <div style="background: #f0f0ff; padding: 24px; border-radius: 12px; margin: 24px 0;">
                    <h3 style="margin: 0 0 12px; color: #6366f1;">Quick Start:</h3>
                    <ol style="color: #64748b; padding-left: 20px;">
                        <li>Add your first learner profile</li>
                        <li>Search for a topic they want to learn (or where they're stuck)</li>
                        <li>Run Gap Analysis to find missing prerequisites</li>
                        <li>Generate a personalized learning path</li>
                    </ol>
                </div>
                <a href="https://app.obiomacare.com" 
                   style="display: inline-block; background: #6366f1; color: white; padding: 16px 32px; 
                          text-decoration: none; border-radius: 8px; font-weight: 600;">
                    Open Dashboard
                </a>
                <p style="margin-top: 32px; color: #94a3b8; font-size: 14px;">
                    Questions? Reply to this email or contact admin@obiomacare.com
                </p>
            </div>
        </div>
        """
        return self._send(to, "Welcome to OBIO 🎯", html)
    
    def send_mastery_update(self, to: str, learner_name: str, topic_name: str, status: str) -> dict:
        status_emoji = {"mastered": "⭐", "in-progress": "🔄", "not-started": "📋"}
        status_color = {"mastered": "#22c55e", "in-progress": "#f59e0b", "not-started": "#64748b"}
        emoji = status_emoji.get(status, "📋")
        color = status_color.get(status, "#64748b")
        
        html = f"""
        <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 40px; background: white;">
                <p style="font-size: 18px; color: #1a1a2e;">Hi there,</p>
                <p style="color: #64748b;">
                    {learner_name} has made progress on <strong>{topic_name}</strong>:
                </p>
                <div style="background: {color}15; padding: 24px; border-radius: 12px; text-align: center; margin: 24px 0; border: 2px solid {color}30;">
                    <div style="font-size: 48px; margin-bottom: 12px;">{emoji}</div>
                    <div style="font-size: 24px; font-weight: 700; color: {color}; text-transform: capitalize;">{status.replace('-', ' ')}</div>
                </div>
                <a href="https://app.obiomacare.com/learners" 
                   style="display: inline-block; background: #6366f1; color: white; padding: 14px 28px; 
                          text-decoration: none; border-radius: 8px; font-weight: 600;">
                    View Progress
                </a>
            </div>
        </div>
        """
        return self._send(to, f"{learner_name} updated mastery: {topic_name}", html)
    
    def send_weekly_report(self, to: str, learner_name: str, stats: dict) -> dict:
        mastered = stats.get("mastered", 0)
        in_progress = stats.get("in_progress", 0)
        gaps = stats.get("gaps", 0)
        
        html = f"""
        <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 40px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 24px;">📊 Weekly Progress Report</h1>
                <p style="margin: 8px 0 0; opacity: 0.9;">{learner_name} — {stats.get('week_start', 'This week')}</p>
            </div>
            <div style="padding: 40px; background: white;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px;">
                    <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 32px; font-weight: 800; color: #22c55e;">{mastered}</div>
                        <div style="color: #64748b; font-size: 14px;">Mastered</div>
                    </div>
                    <div style="background: #fffbeb; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 32px; font-weight: 800; color: #f59e0b;">{in_progress}</div>
                        <div style="color: #64748b; font-size: 14px;">In Progress</div>
                    </div>
                    <div style="background: #fef2f2; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 32px; font-weight: 800; color: #ef4444;">{gaps}</div>
                        <div style="color: #64748b; font-size: 14px;">Gaps</div>
                    </div>
                </div>
                <a href="https://app.obiomacare.com/analytics" 
                   style="display: inline-block; background: #6366f1; color: white; padding: 14px 28px; 
                          text-decoration: none; border-radius: 8px; font-weight: 600;">
                    View Full Analytics
                </a>
            </div>
        </div>
        """
        return self._send(to, f"Weekly Report: {learner_name}", html)

    def send_password_reset(self, to: str, name: str, reset_token: str) -> dict:
        """Send password reset email with secure link."""
        reset_url = f"https://app.obiomacare.com/reset-password?token={reset_token}"
        html = f"""
        <div style="font-family: Inter, -apple-system, sans-serif; max-width: 600px; margin: 0 auto; color: #1f1c19;">
            <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 48px 40px; text-align: center; color: white; border-radius: 0 0 24px 24px;">
                <div style="font-size: 40px; margin-bottom: 16px;">🔐</div>
                <h1 style="margin: 0; font-size: 24px; font-weight: 700;">Reset Your Password</h1>
                <p style="margin: 8px 0 0; opacity: 0.9; font-size: 15px;">We received a request to reset your OBIO password.</p>
            </div>
            <div style="padding: 40px; background: #faf9f7;">
                <p style="font-size: 16px; color: #5c554f; line-height: 1.6;">
                    Hi {name or "there"},
                </p>
                <p style="color: #7c756d; line-height: 1.6;">
                    Click the button below to set a new password. This link is valid for 24 hours and can only be used once.
                </p>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{reset_url}"
                       style="display: inline-block; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white;
                              padding: 16px 40px; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 16px;
                              box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);">
                        Reset Password
                    </a>
                </div>
                <p style="color: #a8a198; font-size: 13px; line-height: 1.5;">
                    Or copy and paste this link into your browser:<br>
                    <span style="color: #6366f1; word-break: break-all;">{reset_url}</span>
                </p>
                <div style="border-top: 1px solid #e8e5df; margin-top: 32px; padding-top: 24px;">
                    <p style="color: #a8a198; font-size: 13px; margin: 0;">
                        If you didn't request this reset, you can safely ignore this email. Your password won't change.
                    </p>
                </div>
            </div>
        </div>
        """
        text = f"""Reset Your OBIO Password\n\nHi {name or 'there'},\n\nWe received a request to reset your OBIO password.\n\nClick this link to reset: {reset_url}\n\nThis link is valid for 24 hours.\n\nIf you didn't request this, ignore this email."""
        return self._send(to, "Reset your OBIO password", html, text)

email_service = EmailService()
