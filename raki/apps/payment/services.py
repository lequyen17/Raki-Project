import uuid
import logging
from django.conf import settings
from django.db import transaction
from apps.payment.registry import PaymentGatewayRegistry
from apps.payment.repositories import WalletRepository, PaymentRepository

logger = logging.getLogger(__name__)


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

    @staticmethod
    def get_payment_histories(user):
        payments = WalletRepository.get_payment_histories(user)
        return {
            "results": [
                {
                    "id": item.id,
                    "amount_vnd": str(item.amount_vnd),
                    "coin_received": item.coin_received,
                    "status": item.status,
                    "created_at": item.created_at,
                }
                for item in payments
            ]
        }


class PaymentService:

    @staticmethod
    def create_topup(user, amount, gateway_type, **kwargs):
        try:
            amount = int(amount)
            if amount < 10000:
                return False, "Minimum top up amount is 10,000 VND", None
        except (ValueError, TypeError):
            return False, "Invalid amount format", None

        payment_history = PaymentRepository.create_payment(
            user=user,
            amount_vnd=amount,
            coin_received=amount,
            status="pending"
        )

        order_id = f"{payment_history.id}_{uuid.uuid4().hex[:8]}"
        gateway = PaymentGatewayRegistry.get(gateway_type)

        try:
            if gateway_type == "vnpay":
                result = gateway.create_payment(
                    amount=amount,
                    order_id=order_id,
                    ipaddr=kwargs.get("ipaddr"),
                    return_url=kwargs.get("return_url")
                )
                return True, "Success", {
                    "payUrl": result["pay_url"],
                    "paymentId": payment_history.id,
                    "orderId": order_id
                }

            elif gateway_type == "momo":
                result = gateway.create_payment(
                    amount=amount,
                    order_id=order_id,
                    redirect_url=kwargs.get("redirect_url"),
                    ipn_url=kwargs.get("ipn_url")
                )
                return True, "Success", {
                    "payUrl": result["pay_url"],
                    "paymentId": payment_history.id,
                    "orderId": order_id
                }

            elif gateway_type == "stripe":
                result = gateway.create_payment(
                    amount=amount,
                    order_id=order_id,
                    success_url=kwargs.get("success_url"),
                    cancel_url=kwargs.get("cancel_url"),
                    user_email=user.email or None
                )
                return True, "Success", {
                    "sessionId": result["session_id"],
                    "paymentId": payment_history.id,
                    "orderId": order_id,
                    "payUrl": result["pay_url"]
                }
            else:
                return False, "Unsupported gateway", None
        except Exception as e:
            logger.error("Payment creation failed: %s", str(e))
            return False, str(e), None

    @staticmethod
    def process_momo_callback(order_id, result_code):
        if not order_id:
            return False, "Missing orderId"

        if result_code == "0":
            try:
                payment_id = int(order_id.split("_")[0])
                with transaction.atomic():
                    payment = PaymentRepository.get_payment_by_id(payment_id, for_update=True)
                    if payment.status == "pending":
                        PaymentRepository.mark_payment_completed(payment)
                return True, "Success"
            except Exception as e:
                logger.error("Error processing momo payment %s: %s", order_id, str(e))
                return False, f"Internal error: {str(e)}"
        else:
            logger.warning(f"MoMo payment failed or canceled for order {order_id}")
            return False, "Payment failed from MoMo"

    @staticmethod
    def process_vnpay_ipn(input_data):
        gateway = PaymentGatewayRegistry.get("vnpay")
        
        if not input_data:
            return {"RspCode": "99", "Message": "Invalid request"}

        if not gateway.verify_payment(input_data):
            return {"RspCode": "97", "Message": "Invalid Signature"}

        order_id = input_data.get("vnp_TxnRef")
        vnp_ResponseCode = input_data.get("vnp_ResponseCode")
        
        try:
            payment_id = int(order_id.split("_")[0])
            payment = PaymentRepository.get_payment_by_id(payment_id)
        except Exception:
            return {"RspCode": "01", "Message": "Order not found"}

        if payment.status != "pending":
            return {"RspCode": "02", "Message": "Order Already Update"}

        vnp_Amount = int(input_data.get("vnp_Amount", 0))
        if vnp_Amount != payment.amount_vnd * 100:
            return {"RspCode": "04", "Message": "invalid amount"}

        if vnp_ResponseCode == "00":
            with transaction.atomic():
                payment = PaymentRepository.get_payment_by_id(payment_id, for_update=True)
                if payment.status == "pending":
                    PaymentRepository.mark_payment_completed(payment)
            return {"RspCode": "00", "Message": "Confirm Success"}
        else:
            PaymentRepository.update_payment_status(payment, "failed")
            return {"RspCode": vnp_ResponseCode, "Message": "Payment Failed"}

    @staticmethod
    def verify_vnpay_result(input_data):
        gateway = PaymentGatewayRegistry.get("vnpay")
        vnp_ResponseCode = input_data.get("vnp_ResponseCode")
        vnp_TxnRef = input_data.get("vnp_TxnRef")
        vnp_SecureHash = input_data.get("vnp_SecureHash")
        
        if vnp_ResponseCode and vnp_TxnRef and vnp_SecureHash:
            valid = gateway.verify_payment(input_data)
            is_success = valid and vnp_ResponseCode == "00"
            return valid, is_success
        return False, False

    @staticmethod
    def process_stripe_webhook(payload, sig_header, webhook_secret):
        if webhook_secret:
            gateway = PaymentGatewayRegistry.get("stripe")
            if not gateway.verify_payment({"payload": payload, "sig_header": sig_header}):
                return False, "Signature verification failed"

        import json
        try:
            event_dict = json.loads(payload)
        except Exception:
            return False, "Failed to parse JSON"

        event_type = event_dict.get("type")
        if event_type == "checkout.session.completed":
            session_data = event_dict.get("data", {}).get("object", {})
            order_id = session_data.get("metadata", {}).get("order_id")

            if not order_id:
                return True, "Missing order_id"

            try:
                payment_id = int(order_id.split("_")[0])
            except (ValueError, IndexError):
                return True, "Invalid payment_id format"

            with transaction.atomic():
                try:
                    payment = PaymentRepository.get_payment_by_id(payment_id, for_update=True)
                    if payment.status == "pending":
                        PaymentRepository.mark_payment_completed(payment)
                except Exception:
                    return True, "Payment not found"

        return True, "Success"
