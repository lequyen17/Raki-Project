import logging

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payment.repositories import WalletRepository
from apps.payment.serializers import (
    StripeTopupResponseSerializer,
    VnpayTopupRequestSerializer,
)
from apps.payment.services import PaymentServiceClient

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Payment"],
    summary="Create Stripe Checkout Session for top‑up",
    request=VnpayTopupRequestSerializer,
    responses={200: StripeTopupResponseSerializer},
)
class StripeTopupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount_val = request.data.get("amount")

        redirect_url = request.data.get(
            "redirectUrl",
            request.build_absolute_uri("/app/wallet"),
        )
        success_url = f"{redirect_url}?stripe=success&amount={amount_val}&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{redirect_url}?stripe=cancel"

        success, message, data = PaymentServiceClient.create_topup(
            user=request.user,
            amount=amount_val,
            gateway_type="stripe",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        if not success:
            return Response({"error": message}, status=400)

        return Response(data)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        # Forward sang Payment Service
        result = PaymentServiceClient.process_stripe_webhook(payload, sig_header)

        if not result.get("success"):
            # Nếu chỉ là event type không xử lý, vẫn trả 200
            if result.get("message") in ("Unhandled event type", "Missing order_id"):
                return HttpResponse(status=200)
            logger.error(f"Stripe webhook error: {result.get('message')}")
            return HttpResponse(status=400)

        # Cộng coin nếu thành công
        if result.get("userId") and result.get("coinReceived"):
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
                logger.error("Failed to add coin for user %s: %s", result["userId"], str(e))

        return HttpResponse(status=200)
