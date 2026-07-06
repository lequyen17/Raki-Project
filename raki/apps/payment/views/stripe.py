import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payment.serializers import (
    StripeTopupResponseSerializer,
    VnpayTopupRequestSerializer,
)
from apps.payment.services import PaymentService

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


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
