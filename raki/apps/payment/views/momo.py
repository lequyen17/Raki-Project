import logging

from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payment.serializers import (
    VnpayTopupRequestSerializer,
    VnpayTopupResponseSerializer,
)
from apps.payment.services import PaymentService

logger = logging.getLogger(__name__)

FRONTEND_WALLET_URL = "https://trilogy-had-train.ngrok-free.dev/app/wallet"


@extend_schema(
    tags=["Payment"],
    summary="Create MoMo top‑up transaction",
    request=VnpayTopupRequestSerializer,
    responses={200: VnpayTopupResponseSerializer},
)
class MomoTopupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount_val = request.data.get("amount")

        success, message, data = PaymentService.create_topup(
            user=request.user,
            amount=amount_val,
            gateway_type="momo",
            redirect_url=request.build_absolute_uri("/api/wallet/topup/momo/result/"),
            ipn_url=request.build_absolute_uri("/api/wallet/topup/momo/ipn/"),
        )

        if not success:
            return Response({"error": message}, status=400)

        return Response(data)


@extend_schema(
    tags=["Payment"],
    summary="MoMo payment result callback",
    responses={200: "application/json"},
)
class MomoResultView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("MoMo result callback received: %s", request.GET.dict())
        result_code = request.GET.get("resultCode")
        order_id = request.GET.get("orderId")
        amount = request.GET.get("amount", "0")

        success, message = PaymentService.process_momo_callback(order_id, result_code)

        if success:
            return redirect(f"{FRONTEND_WALLET_URL}?momo=success&amount={amount}")

        return redirect(f"{FRONTEND_WALLET_URL}?momo=failed")
