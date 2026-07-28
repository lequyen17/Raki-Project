from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from apps.payment.serializers import (
    CoinHistoryListResponseSerializer,
    PaymentHistoryListResponseSerializer,
    WalletSummarySerializer,
)
from apps.payment.services import PaymentServiceClient, WalletService
from rest_framework import status as http_status


@extend_schema(
    tags=["Wallet"],
    summary="Số dư coin hiện tại",
    responses={200: WalletSummarySerializer},
)
class WalletSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = WalletService.get_wallet_summary(request.user)
        return ApiResponse(data=data)


@extend_schema(
    tags=["Wallet"],
    summary="Lịch sử biến động coin",
    responses={200: CoinHistoryListResponseSerializer},
)
class CoinHistoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = WalletService.get_coin_histories(request.user)
        return ApiResponse(data=data)


@extend_schema(
    tags=["Wallet"],
    summary="Lịch sử nạp tiền",
    responses={200: PaymentHistoryListResponseSerializer},
)
class PaymentHistoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        success, message, data = PaymentServiceClient.get_payment_histories(
            request.user
        )
        if not success:
            return ApiResponse(
                data={"results": []},
                message=message,
                status="error",
                status_code=http_status.HTTP_502_BAD_GATEWAY,
            )
        return ApiResponse(data=data)
