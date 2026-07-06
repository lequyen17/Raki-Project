from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import logging

from core.utils.api_response import ApiResponse

logger = logging.getLogger(__name__)

from apps.payment.serializers import (
    WalletSummarySerializer,
    CoinHistoryListResponseSerializer,
    PaymentHistoryListResponseSerializer,
    VnpayTopupRequestSerializer,
    VnpayTopupResponseSerializer,
    VnpayIpnResponseSerializer,
    StripeTopupResponseSerializer,
)

from apps.payment.services import WalletService, PaymentService


# Wallet endpoints
@extend_schema(
    tags=["Wallet"],
    summary="Số dư coin hiện tại",
    responses={200: WalletSummarySerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet_summary(request):
    data = WalletService.get_wallet_summary(request.user)
    return ApiResponse(data=data)


@extend_schema(
    tags=["Wallet"],
    summary="Lịch sử biến động coin",
    responses={200: CoinHistoryListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def coin_histories(request):
    data = WalletService.get_coin_histories(request.user)
    return ApiResponse(data=data)


@extend_schema(
    tags=["Wallet"],
    summary="Lịch sử nạp tiền",
    responses={200: PaymentHistoryListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_histories(request):
    data = WalletService.get_payment_histories(request.user)
    return ApiResponse(data=data)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# VNPay top‑up endpoint
@extend_schema(
    tags=["Payment"],
    summary="Create VNPay top‑up transaction",
    request=VnpayTopupRequestSerializer,
    responses={200: VnpayTopupResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vnpay_topup(request):
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


# MoMo top‑up endpoint (POST)
@extend_schema(
    tags=["Payment"],
    summary="Create MoMo top‑up transaction",
    request=VnpayTopupRequestSerializer,
    responses={200: VnpayTopupResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def momo_topup(request):
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


# MoMo result endpoint (GET)
@extend_schema(
    tags=["Payment"],
    summary="MoMo payment result callback",
    responses={200: "application/json"},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def momo_result(request):
    logger.info("MoMo result callback received: %s", request.GET.dict())
    result_code = request.GET.get("resultCode")
    order_id = request.GET.get("orderId")
    amount = request.GET.get("amount", "0")

    FRONTEND_WALLET_URL = "https://trilogy-had-train.ngrok-free.dev/app/wallet"

    success, message = PaymentService.process_momo_callback(order_id, result_code)

    if success:
        return redirect(f"{FRONTEND_WALLET_URL}?momo=success&amount={amount}")

    return redirect(f"{FRONTEND_WALLET_URL}?momo=failed")


# VNPay IPN endpoint
@extend_schema(
    tags=["Payment"],
    summary="VNPay IPN (Instant Payment Notification) endpoint",
    responses={200: VnpayIpnResponseSerializer},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def vnpay_ipn(request):
    print("\n=== [VNPay IPN Request GET Data] ===")
    print(request.GET.dict())
    print("=====================================\n")

    input_data = request.GET
    result_data = PaymentService.process_vnpay_ipn(input_data.dict())

    return Response(result_data)


# Result page (hidden from API docs)
@api_view(["GET"])
@permission_classes([AllowAny])
def vnpay_result(request):
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


# Stripe top‑up endpoint (POST)
@extend_schema(
    tags=["Payment"],
    summary="Create Stripe Checkout Session for top‑up",
    request=VnpayTopupRequestSerializer,
    responses={200: StripeTopupResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def stripe_topup(request):
    amount_val = request.data.get("amount")

    redirect_url = request.data.get(
        "redirectUrl",
        request.build_absolute_uri("/app/wallet"),
    )
    success_url = f"{redirect_url}?stripe=success&amount={amount_val}&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{redirect_url}?stripe=cancel"

    success, message, data = PaymentService.create_topup(
        user=request.user,
        amount=amount_val,
        gateway_type="stripe",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    if not success:
        return Response({"error": message}, status=400)

    return Response(data)


# Stripe Webhook endpoint (POST)
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    success, message = PaymentService.process_stripe_webhook(
        payload, sig_header, webhook_secret
    )

    if not success:
        logger.error(f"Stripe webhook error: {message}")
        return HttpResponse(status=400)

    return HttpResponse(status=200)
