import logging

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payment.serializers import (
    VnpayIpnResponseSerializer,
    VnpayTopupRequestSerializer,
    VnpayTopupResponseSerializer,
)
from apps.payment.services import PaymentService
from apps.payment.views.utils import get_client_ip

logger = logging.getLogger(__name__)


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

        success, message, data = PaymentService.create_topup(
            user=request.user,
            amount=amount_val,
            gateway_type="vnpay",
            ipaddr=get_client_ip(request),
            return_url=request.data.get("redirectUrl"),
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
        print("\n=== [VNPay IPN Request GET Data] ===")
        print(request.GET.dict())
        print("=====================================\n")

        input_data = request.GET
        result_data = PaymentService.process_vnpay_ipn(input_data.dict())

        return Response(result_data)


class VnpayResultView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("\n=== [VNPay RESULT Request GET Data] ===")
        print(request.GET.dict())
        print("========================================\n")

        valid, is_success = PaymentService.verify_vnpay_result(request.GET.dict())

        context = {
            "valid": valid,
            "status": valid,
            "message": "Missing payment information.",
        }

        if (
            request.GET.get("vnp_ResponseCode")
            and request.GET.get("vnp_TxnRef")
            and request.GET.get("vnp_SecureHash")
        ):
            if is_success:
                context["is_success"] = True
                context["message"] = "Thanh toán thành công!"
            else:
                context["message"] = "Thanh toán không thành công. Vui lòng thử lại."

        return render(request, "payment/result.html", context)
