import logging
import requests
from django.conf import settings
from apps.payment.repositories import WalletRepository

logger = logging.getLogger(__name__)

PAYMENT_SERVICE_URL = getattr(
    settings, "PAYMENT_SERVICE_URL", "http://payment-service:8080"
)


class WalletService:

    @staticmethod
    def get_wallet_summary(user):
        return {
            "coin_balance": WalletRepository.get_coin_balance(user),
        }

    @staticmethod
    def get_coin_histories(user):
        histories = WalletRepository.get_coin_histories(user)
        return {
            "results": [
                {
                    "id": item.id,
                    "amount": item.amount,
                    "reason": item.reason,
                    "created_at": item.created_at,
                }
                for item in histories
            ]
        }


class PaymentServiceClient:
    """
    Client gọi HTTP đến Payment Service (Spring Boot) qua Docker internal network.
    Raki backend là orchestrator — gọi Payment Service rồi tự xử lý cộng coin.
    """

    @staticmethod
    def create_topup(user, amount, gateway_type, **kwargs):
        """
        Tạo giao dịch nạp tiền qua Payment Service.
        Returns: (success, message, data)
        """
        payload = {
            "userId": user.id,
            "amount": int(amount),
            "provider": gateway_type.upper(),
        }

        # Gateway-specific params
        if gateway_type == "vnpay":
            payload["ipaddr"] = kwargs.get("ipaddr")
            payload["returnUrl"] = kwargs.get("return_url")
        elif gateway_type == "momo":
            payload["redirectUrl"] = kwargs.get("redirect_url")
            payload["ipnUrl"] = kwargs.get("ipn_url")
        elif gateway_type == "stripe":
            payload["successUrl"] = kwargs.get("success_url")
            payload["cancelUrl"] = kwargs.get("cancel_url")
            payload["userEmail"] = user.email or None

        try:
            resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/payment/create",
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()

            if result.get("success"):
                data = result.get("data", {})
                return True, "Success", data
            else:
                return False, result.get("message", "Payment creation failed"), None
        except requests.Timeout:
            logger.error("Payment Service timeout for create_topup")
            return False, "Payment service timeout", None
        except Exception as e:
            logger.error("Payment creation failed: %s", str(e))
            return False, str(e), None

    @staticmethod
    def get_payment_histories(user):
        """
        Lấy lịch sử nạp tiền từ Payment Service.
        Returns: (success, message, data) với data = {"results": [...]}
        """
        try:
            resp = requests.get(
                f"{PAYMENT_SERVICE_URL}/api/payment/history/{user.id}",
                timeout=10,
            )
            resp.raise_for_status()
            result = resp.json()

            if not result.get("success"):
                return False, result.get("message", "Failed to load payment history"), None

            items = []
            for item in result.get("data") or []:
                items.append(
                    {
                        "id": item.get("id"),
                        "amount_vnd": item.get("amountVnd"),
                        "coin_received": item.get("coinReceived"),
                        "provider": item.get("provider"),
                        "status": item.get("status"),
                        "created_at": item.get("createdAt"),
                    }
                )
            return True, "Success", {"results": items}
        except requests.Timeout:
            logger.error("Payment Service timeout for get_payment_histories")
            return False, "Payment service timeout", None
        except Exception as e:
            logger.error(
                "Failed to get payment histories from Payment Service: %s", str(e)
            )
            return False, str(e), None

    @staticmethod
    def process_vnpay_ipn(params):
        """
        Forward VNPay IPN params sang Payment Service để verify + update.
        Returns: dict với success, userId, coinReceived, rspCode, message
        """
        try:
            resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/payment/vnpay/ipn",
                json=params,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("Error forwarding VNPay IPN to Payment Service: %s", str(e))
            return {
                "success": False,
                "rspCode": "99",
                "message": f"Internal error: {str(e)}",
            }

    @staticmethod
    def verify_vnpay_result(params):
        """
        Forward VNPay result params sang Payment Service để verify signature.
        Returns: dict với success, message
        """
        try:
            resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/payment/vnpay/verify-result",
                json=params,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("Error verifying VNPay result: %s", str(e))
            return {"success": False, "message": "verification_error"}

    @staticmethod
    def process_momo_callback(order_id, result_code):
        """
        Forward MoMo callback sang Payment Service.
        Returns: dict với success, userId, coinReceived, message
        """
        try:
            resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/payment/momo/callback",
                json={"orderId": order_id, "resultCode": str(result_code)},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(
                "Error forwarding MoMo callback to Payment Service: %s", str(e)
            )
            return {"success": False, "message": f"Internal error: {str(e)}"}

    @staticmethod
    def process_stripe_webhook(payload, sig_header):
        """
        Forward Stripe webhook sang Payment Service.
        Returns: dict với success, userId, coinReceived, message
        """
        try:
            resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/payment/stripe/webhook",
                json={"payload": payload, "sigHeader": sig_header},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(
                "Error forwarding Stripe webhook to Payment Service: %s", str(e)
            )
            return {"success": False, "message": f"Internal error: {str(e)}"}
