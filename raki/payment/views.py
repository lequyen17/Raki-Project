from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import logging
from django.shortcuts import redirect

logger = logging.getLogger(__name__)
import uuid
import requests
import hmac
import hashlib
from django.db import transaction

from payment.serializers import (
    WalletSummarySerializer,
    CoinHistoryListResponseSerializer,
    PaymentHistoryListResponseSerializer,
    VnpayTopupRequestSerializer,
    VnpayTopupResponseSerializer,
    VnpayIpnResponseSerializer,
    # MoMo serializer will be added later (reuse VnpayTopupResponseSerializer)
)

from payment.services import WalletService
from payment.models import CoinHistory, PaymentHistory


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
    return Response(data)


@extend_schema(
    tags=["Wallet"],
    summary="Lịch sử biến động coin",
    responses={200: CoinHistoryListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def coin_histories(request):
    data = WalletService.get_coin_histories(request.user)
    return Response(data)


@extend_schema(
    tags=["Wallet"],
    summary="Lịch sử nạp tiền",
    responses={200: PaymentHistoryListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_histories(request):
    data = WalletService.get_payment_histories(request.user)
    return Response(data)


# Helper to get client IP (kept for future use)
from datetime import datetime
from payment.vnpay import vnpay


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# VNPay top‑up endpoint
# ---------------------------------------------------
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
    if not amount_val:
        return Response({"error": "Amount is required"}, status=400)
    try:
        amount = int(amount_val)
        if amount < 10000:
            return Response(
                {"error": "Minimum top up amount is 10,000 VND"}, status=400
            )
    except (ValueError, TypeError):
        return Response({"error": "Invalid amount format"}, status=400)

    payment_history = PaymentHistory.objects.create(
        user=request.user,
        amount_vnd=amount,
        coin_received=amount,
        status="pending",
    )

    from zoneinfo import ZoneInfo
    from datetime import datetime, timedelta

    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    now = datetime.now(tz)
    expire = now + timedelta(minutes=60)

    # Unique transaction reference (max 32 chars)
    order_id = f"{payment_history.id}_{uuid.uuid4().hex[:8]}"
    # Hard‑coded public Vietnamese IP for testing
    ipaddr = "14.226.5.81"

    vnp = vnpay()
    vnp.requestData["vnp_Version"] = "2.1.0"
    vnp.requestData["vnp_Command"] = "pay"
    vnp.requestData["vnp_TmnCode"] = "DZLOX1ST"
    vnp.requestData["vnp_Amount"] = amount * 100
    vnp.requestData["vnp_CurrCode"] = "VND"
    vnp.requestData["vnp_TxnRef"] = order_id
    vnp.requestData["vnp_OrderInfo"] = f"Thanh toan don hang {order_id}"
    vnp.requestData["vnp_OrderType"] = "other"
    vnp.requestData["vnp_Locale"] = "vn"
    vnp.requestData["vnp_CreateDate"] = now.strftime("%Y%m%d%H%M%S")
    vnp.requestData["vnp_ExpireDate"] = expire.strftime("%Y%m%d%H%M%S")
    vnp.requestData["vnp_IpAddr"] = ipaddr
    vnp.requestData["vnp_ReturnUrl"] = request.build_absolute_uri(
        "/api/wallet/topup/vnpay/result/"
    )

    vnpay_payment_url = vnp.get_payment_url(
        "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
        "FRD8HSODHRZU3MUSVYOE0O14J48Z190J",
    )

    serializer = VnpayTopupResponseSerializer(
        data={
            "payUrl": vnpay_payment_url,
            "paymentId": payment_history.id,
            "orderId": order_id,
        }
    )
    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# MoMo top‑up endpoint (POST)
@extend_schema(
    tags=["Payment"],
    summary="Create MoMo top‑up transaction",
    request=VnpayTopupRequestSerializer,  # reuse same request serializer (amount only)
    responses={200: VnpayTopupResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def momo_topup(request):
    amount_val = request.data.get("amount")
    if not amount_val:
        return Response({"error": "Amount is required"}, status=400)
    try:
        amount = int(amount_val)
        if amount < 10000:
            return Response(
                {"error": "Minimum top up amount is 10,000 VND"}, status=400
            )
    except (ValueError, TypeError):
        return Response({"error": "Invalid amount format"}, status=400)

    payment_history = PaymentHistory.objects.create(
        user=request.user,
        amount_vnd=amount,
        coin_received=amount,
        status="pending",
    )

    # Generate order identifiers similar to VNPay
    order_id = f"{payment_history.id}_{uuid.uuid4().hex[:8]}"
    redirect_url = request.build_absolute_uri("/api/wallet/topup/momo/result/")
    ipn_url = request.build_absolute_uri("/api/wallet/topup/momo/ipn/")

    # Use helper to create MoMo payment URL
    from .momo import create_momo_payment

    try:
        pay_url = create_momo_payment(amount, redirect_url, ipn_url, order_id)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    serializer = VnpayTopupResponseSerializer(
        data={
            "payUrl": pay_url,
            "paymentId": payment_history.id,
            "orderId": order_id,
        }
    )
    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# MoMo result endpoint (GET) – simple JSON response confirming payment status
@extend_schema(
    tags=["Payment"],
    summary="MoMo payment result callback",
    responses={200: "application/json"},
)
def momo_result(request):
    logger.info("MoMo result callback received: %s", request.GET.dict())
    result_code = request.GET.get("resultCode")
    order_id = request.GET.get("orderId")

    response_data = {
        "valid": False,
        "status": "failed",
        "message": "Payment verification failed",
    }

    if not order_id:
        response_data["message"] = "Missing orderId"
        return Response(response_data, status=400)

    # ĐỊNH NGHĨA URL FRONTEND CỦA BẠN (Thay đổi domain cho đúng thực tế)
    # Vì đây là API Backend, redirect('/app/wallet') sẽ bắt trình duyệt tìm đến domain-backend/app/wallet
    FRONTEND_WALLET_URL = "https://trilogy-had-train.ngrok-free.dev/app/wallet"  # Hoặc domain production của bạn

    if result_code == "0":
        try:
            payment_id = int(order_id.split("_")[0])

            # ĐƯA TRANSACTION ATOMIC LÊN TRƯỚC KHI GET SELECT FOR UPDATE
            with transaction.atomic():
                try:
                    payment = PaymentHistory.objects.select_for_update().get(
                        id=payment_id
                    )
                except PaymentHistory.DoesNotExist:
                    logger.error(
                        f"PaymentHistory ID {payment_id} không tồn tại trong DB!"
                    )
                    response_data["message"] = "Order not found in database"
                    return Response(response_data, status=400)

                if payment.status == "pending":
                    payment.status = "completed"
                    payment.save(update_fields=["status"])

                    profile = payment.user.profile
                    profile.coin_balance += payment.coin_received
                    profile.save(update_fields=["coin_balance"])

                    CoinHistory.objects.create(
                        user=payment.user,
                        amount=payment.coin_received,
                        reason="TOPUP",
                    )

            # Thành công -> Redirect về trang Wallet của Frontend
            return redirect(FRONTEND_WALLET_URL)

        except Exception as e:
            logger.error("Lỗi xử lý thanh toán %s: %s", order_id, str(e))
            response_data["message"] = f"Internal error: {str(e)}"
            return Response(response_data, status=500)

    else:
        # Thanh toán thất bại từ phía MoMo (resultCode != 0)
        logger.warning(f"MoMo payment failed or canceled for order {order_id}")
        response_data["message"] = "Payment failed from MoMo"
        return Response(response_data, status=400)


# VNPay IPN endpoint
@extend_schema(
    tags=["Payment"],
    summary="VNPay IPN (Instant Payment Notification) endpoint",
    responses={200: VnpayIpnResponseSerializer},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def vnpay_ipn(request):
    # Dòng này sẽ in toàn bộ các tham số VNPay gửi về IPN ra console
    print("\n=== [VNPay IPN Request GET Data] ===")
    print(request.GET.dict())
    print("=====================================\n")
    inputData = request.GET
    if not inputData:
        serializer = VnpayIpnResponseSerializer(
            data={"RspCode": "99", "Message": "Invalid request"}
        )
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    vnp = vnpay()
    vnp.responseData = inputData.dict()
    order_id = inputData.get("vnp_TxnRef")
    vnp_ResponseCode = inputData.get("vnp_ResponseCode")

    # Validate VNPay signature
    if not vnp.validate_response("FRD8HSODHRZU3MUSVYOE0O14J48Z190J"):
        serializer = VnpayIpnResponseSerializer(
            data={"RspCode": "97", "Message": "Invalid Signature"}
        )
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    # Retrieve payment record
    try:
        payment_id = int(order_id.split("_")[0])
        payment_history = PaymentHistory.objects.get(id=payment_id)
    except (ValueError, TypeError, PaymentHistory.DoesNotExist):
        serializer = VnpayIpnResponseSerializer(
            data={"RspCode": "01", "Message": "Order not found"}
        )
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if payment_history.status != "pending":
        serializer = VnpayIpnResponseSerializer(
            data={"RspCode": "02", "Message": "Order Already Update"}
        )
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    vnp_Amount = int(inputData.get("vnp_Amount", 0))
    if vnp_Amount != payment_history.amount_vnd * 100:
        return Response({"RspCode": "04", "Message": "invalid amount"})

    if vnp_ResponseCode == "00":
        with transaction.atomic():
            payment_history = PaymentHistory.objects.select_for_update().get(
                id=payment_id
            )
            if payment_history.status == "pending":
                payment_history.status = "completed"
                payment_history.save(update_fields=["status"])

                profile = payment_history.user.profile
                profile.coin_balance += payment_history.coin_received
                profile.save(update_fields=["coin_balance"])

                CoinHistory.objects.create(
                    user=payment_history.user,
                    amount=payment_history.coin_received,
                    reason="TOPUP",
                )
        serializer = VnpayIpnResponseSerializer(
            data={"RspCode": "00", "Message": "Confirm Success"}
        )
    else:
        payment_history.status = "failed"
        payment_history.save(update_fields=["status"])
        serializer = VnpayIpnResponseSerializer(
            data={"RspCode": vnp_ResponseCode, "Message": "Payment Failed"}
        )

    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# Result page (hidden from API docs)


@api_view(["GET"])
@permission_classes([AllowAny])
def vnpay_result(request):
    print("\n=== [VNPay RESULT Request GET Data] ===")
    print(request.GET.dict())
    print("========================================\n")
    vnp_ResponseCode = request.GET.get("vnp_ResponseCode")
    vnp_TxnRef = request.GET.get("vnp_TxnRef")
    vnp_SecureHash = request.GET.get("vnp_SecureHash")
    context = {
        "valid": False,
        "status": False,
        "message": "Missing payment information.",
    }
    if vnp_ResponseCode and vnp_TxnRef and vnp_SecureHash:
        vnp = vnpay()
        vnp.responseData = request.GET.dict()
        valid = vnp.validate_response("FRD8HSODHRZU3MUSVYOE0O14J48Z190J")
        context["valid"] = valid
        if valid and vnp_ResponseCode == "00":
            context["is_success"] = True
            context["message"] = "Thanh toán thành công!"
        else:
            context["message"] = "Thanh toán không thành công. Vui lòng thử lại."
    return render(request, "payment/result.html", context)
