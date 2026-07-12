"""
Stripe Payment Integration for MasteryGraph
Handles checkout sessions, subscriptions, and webhooks.
"""
import os
import stripe
from datetime import datetime
from typing import Optional, Dict, Any

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "https://app.obiomacare.com/dashboard")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "https://app.obiomacare.com/pricing")

# Product/Price IDs (can be created via Stripe Dashboard or API)
# These are environment variables that should be set after creating products in Stripe
STRIPE_PRICE_FAMILY = os.getenv("STRIPE_PRICE_FAMILY", "")  # $12/month
STRIPE_PRICE_EDUCATOR = os.getenv("STRIPE_PRICE_EDUCATOR", "")  # $29/month

# Set API key if available
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

class StripePaymentManager:
    """Manages Stripe payments for MasteryGraph subscriptions."""
    
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = STRIPE_SECRET_KEY
    
    def is_configured(self) -> bool:
        return bool(STRIPE_SECRET_KEY)
    
    def create_checkout_session(self, user_email: str, plan: str, user_id: str) -> Dict[str, Any]:
        """Create a Stripe Checkout Session for subscription."""
        if not self.is_configured():
            raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY environment variable.")
        
        price_id = self._get_price_id(plan)
        if not price_id:
            raise ValueError(f"Price ID not configured for plan: {plan}")
        
        session = self.stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=STRIPE_CANCEL_URL,
            metadata={
                "user_id": user_id,
                "plan": plan,
            },
            subscription_data={
                "metadata": {
                    "user_id": user_id,
                    "plan": plan,
                }
            }
        )
        
        return {
            "session_id": session.id,
            "url": session.url,
        }
    
    def get_subscription_status(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription status from Stripe."""
        if not self.is_configured():
            return {"status": "inactive", "error": "Stripe not configured"}
        
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            return {
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "plan": subscription.get("metadata", {}).get("plan", "unknown"),
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }
        except stripe.error.StripeError as e:
            return {"status": "error", "error": str(e)}
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription at period end."""
        if not self.is_configured():
            raise ValueError("Stripe not configured")
        
        subscription = self.stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return {
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
        }
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events."""
        if not self.is_configured():
            return {"status": "error", "error": "Stripe not configured"}
        
        if not STRIPE_WEBHOOK_SECRET:
            return {"status": "error", "error": "Webhook secret not configured"}
        
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return {"status": "error", "error": "Invalid payload"}
        except stripe.error.SignatureVerificationError:
            return {"status": "error", "error": "Invalid signature"}
        
        # Handle the event
        event_type = event["type"]
        data = event["data"]["object"]
        
        result = {
            "event": event_type,
            "handled": True,
        }
        
        if event_type == "checkout.session.completed":
            # Subscription created
            user_id = data.get("metadata", {}).get("user_id")
            subscription_id = data.get("subscription")
            plan = data.get("metadata", {}).get("plan")
            result.update({
                "user_id": user_id,
                "subscription_id": subscription_id,
                "plan": plan,
                "action": "subscription_activated",
            })
            
        elif event_type == "invoice.payment_succeeded":
            # Payment succeeded
            subscription_id = data.get("subscription")
            result.update({
                "subscription_id": subscription_id,
                "action": "payment_succeeded",
            })
            
        elif event_type == "invoice.payment_failed":
            # Payment failed
            subscription_id = data.get("subscription")
            result.update({
                "subscription_id": subscription_id,
                "action": "payment_failed",
            })
            
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            subscription_id = data.get("id")
            user_id = data.get("metadata", {}).get("user_id")
            result.update({
                "subscription_id": subscription_id,
                "user_id": user_id,
                "action": "subscription_cancelled",
            })
        
        return result
    
    def _get_price_id(self, plan: str) -> Optional[str]:
        """Get Stripe price ID for a plan."""
        prices = {
            "family": STRIPE_PRICE_FAMILY,
            "educator": STRIPE_PRICE_EDUCATOR,
        }
        return prices.get(plan.lower(), "")
    
    def create_products_if_needed(self) -> Dict[str, Any]:
        """Create products and prices in Stripe if they don't exist."""
        if not self.is_configured():
            return {"error": "Stripe not configured"}
        
        created = {}
        
        # Family Plan ($12/month)
        if not STRIPE_PRICE_FAMILY:
            product = self.stripe.Product.create(
                name="MasteryGraph Family",
                description="Unlimited learners, full analytics, gap analysis, and personalized plans",
            )
            price = self.stripe.Price.create(
                product=product.id,
                unit_amount=1200,  # $12.00 in cents
                currency="usd",
                recurring={"interval": "month"},
                metadata={"plan": "family"},
            )
            created["family"] = {
                "product_id": product.id,
                "price_id": price.id,
            }
        
        # Educator Plan ($29/month)
        if not STRIPE_PRICE_EDUCATOR:
            product = self.stripe.Product.create(
                name="MasteryGraph Educator",
                description="Everything in Family + classroom management, standards alignment, and priority support",
            )
            price = self.stripe.Price.create(
                product=product.id,
                unit_amount=2900,  # $29.00 in cents
                currency="usd",
                recurring={"interval": "month"},
                metadata={"plan": "educator"},
            )
            created["educator"] = {
                "product_id": product.id,
                "price_id": price.id,
            }
        
        return created

# Singleton
_stripe_mgr = None

def get_stripe_manager():
    global _stripe_mgr
    if _stripe_mgr is None:
        _stripe_mgr = StripePaymentManager()
    return _stripe_mgr
