import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payment.repositories import WalletRepository
from apps.payment.serializers import (
    VnpayIpnResponseSerializer,
    VnpayTopupRequestSerializer,
    VnpayTopupResponseSerializer,
)
from apps.payment.services import PaymentServiceClient
from apps.payment.views.utils import build_public_uri, get_client_ip

logger = logging.getLogger(__name__)
FRONTEND_WALLET_URL = settings.FRONTEND_WALLET_URL


def _credit_coins_from_vnpay_result(result):
    if not (
        result.get("success")
        and result.get("userId")
        and result.get("coinReceived")
    ):
        return

    try:
        user = User.objects.get(id=result["userId"])
        WalletRepository.add_coin(
            user=user,
            amount=result["coinReceived"],
            reason="TOPUP",
        )
    except User.DoesNotExist:
        logger.error("User %s not found for coin addition", result["userId"])
    except Exception as e:
        logger.error(
            "Failed to add coin for user %s: %s", result["userId"], str(e)
        )


def _is_vnpay_payment_successful(params, result):
    if result.get("success"):
        return True
    return (
        params.get("vnp_ResponseCode") == "00"
        and result.get("rspCode") == "00"
    )


def _handle_vnpay_callback(params):
    result = PaymentServiceClient.process_vnpay_ipn(params)
    _credit_coins_from_vnpay_result(result)
    return result


@extend_schema(
    tags=["Payment"],
    summary="Create VNPay top‑up transaction",
    request=VnpayTopupRequestSerializer,
    responses={200: VnpayTopupResponseSerializer},
)
class VnpayTopupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount_val = request.data.get("amount")
        result_url = build_public_uri(request, "/api/wallet/topup/vnpay/result/")
        ipn_url = build_public_uri(request, "/api/wallet/topup/vnpay/ipn/")

        logger.info(
            "Creating VNPay payment. returnUrl=%s ipnUrl=%s "
            "(configure ipnUrl in VNPay merchant portal)",
            result_url,
            ipn_url,
        )

        success, message, data = PaymentServiceClient.create_topup(
            user=request.user,
            amount=amount_val,
            gateway_type="vnpay",
            ipaddr=get_client_ip(request),
            return_url=result_url,
        )

        if not success:
            return Response({"error": message}, status=400)

        return Response(data)


@extend_schema(
    tags=["Payment"],
    summary="VNPay IPN (Instant Payment Notification) endpoint",
    responses={200: VnpayIpnResponseSerializer},
)
class VnpayIpnView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        input_data = request.GET.dict()
        logger.info("VNPay IPN received: %s", input_data)
        result = _handle_vnpay_callback(input_data)

        return Response(
            {
                "RspCode": result.get("rspCode", "99"),
                "Message": result.get("message", "Unknown error"),
            }
        )


class VnpayResultView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        params = request.GET.dict()
        logger.info("VNPay result callback received: %s", params)

        # Fallback when VNPay IPN has not reached the server yet.
        result = _handle_vnpay_callback(params)

        amount = request.GET.get("vnp_Amount", "0")
        try:
            amount_vnd = str(int(amount) // 100)
        except (TypeError, ValueError):
            amount_vnd = "0"

        if _is_vnpay_payment_successful(params, result):
            return redirect(f"{FRONTEND_WALLET_URL}?vnpay=success&amount={amount_vnd}")

        return redirect(f"{FRONTEND_WALLET_URL}?vnpay=failed")
