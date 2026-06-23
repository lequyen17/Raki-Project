import stripe
from typing import Dict, Any

from apps.payment.interfaces import PaymentGatewayInterface


class StripeGateway(PaymentGatewayInterface):
    def __init__(self, secret_key: str, webhook_secret: str = None):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        stripe.api_key = self.secret_key

    def create_payment(self, amount: int, order_id: str, **kwargs) -> Dict[str, Any]:
        success_url = kwargs.get("success_url")
        cancel_url = kwargs.get("cancel_url")
        user_email = kwargs.get("user_email")

        session_params = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price_data": {
                        "currency": "vnd",
                        "product_data": {
                            "name": f"Raki Coin Top-up - {amount:,} VND",
                            "description": f"Order {order_id}",
                        },
                        "unit_amount": amount,
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
        return {
            "pay_url": session.url,
            "session_id": session.id,
        }

    def verify_payment(self, request_data: Any) -> bool:
        """
        Verify Stripe webhook signature.
        request_data should contain 'payload' and 'sig_header'.
        """
        payload = request_data.get("payload")
        sig_header = request_data.get("sig_header")

        if not self.webhook_secret:
            return True

        try:
            stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            return True
        except Exception:
            return False
