from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payment.serializers import (
    CoinHistoryListResponseSerializer,
    PaymentHistoryListResponseSerializer,
    WalletSummarySerializer,
)
from payment.services import WalletService


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
