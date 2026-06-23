import stripe
from django.conf import settings

# Stripe payment helper
# Creates a Stripe Checkout Session for wallet top‑up and returns the session ID.


def create_stripe_checkout_session(amount, success_url, cancel_url, order_id, user_email=None):
    """Create a Stripe Checkout Session for a one‑time wallet top‑up.

    Args:
        amount: Amount in VND (integer).
        success_url: URL to redirect to after successful payment.
        cancel_url: URL to redirect to if user cancels.
        order_id: Internal order reference string.
        user_email: Optional email to prefill in the Checkout form.

    Returns:
        The Stripe Checkout Session object.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session_params = {
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price_data": {
                    "currency": "vnd",
                    "product_data": {
                        "name": f"Raki Coin Top‑up – {amount:,} VND",
                        "description": f"Order {order_id}",
                    },
                    "unit_amount": amount,  # VND is zero‑decimal currency
                },
                "quantity": 1,
            }
        ],
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {
            "order_id": order_id,
        },
    }

    if user_email:
        session_params["customer_email"] = user_email

    session = stripe.checkout.Session.create(**session_params)
    return session
