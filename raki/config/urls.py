"""
URL configuration for raki project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema


class SpectacularElementsView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "elements.html"

    @extend_schema(exclude=True)
    def get(self, request):
        return Response(
            {
                "schema_url": "/api/schema/",
            }
        )


from drf_spectacular.views import SpectacularAPIView

from django.contrib import admin
from django.urls import path

# Sử dụng 'as' để đặt tên riêng cho từng file views
from apps.accounts import views as accounts_views
from apps.deck import views as deck_views
from apps.card import views as card_views
from apps.note import views as note_views
from apps.payment import views as payment_views
from apps.payment.serializers import (
    WalletSummarySerializer,
    CoinHistoryListResponseSerializer,
    PaymentHistoryListResponseSerializer,
    VnpayTopupRequestSerializer,
    VnpayTopupResponseSerializer,
    VnpayIpnResponseSerializer,
    StripeTopupResponseSerializer,
    # MoMo uses same response serializer
)
from core.utils.openapi_common import (
    TokenObtainPairRequestSerializer,
    TokenPairResponseSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

TokenObtainPairView = extend_schema(
    tags=["Auth"],
    summary="Đăng nhập (JWT access + refresh)",
    auth=[],
    request=TokenObtainPairRequestSerializer,
    responses={200: TokenPairResponseSerializer},
)(TokenObtainPairView)

TokenRefreshView = extend_schema(
    tags=["Auth"],
    summary="Làm mới access token",
    auth=[],
    request=TokenRefreshRequestSerializer,
    responses={200: TokenRefreshResponseSerializer},
)(TokenRefreshView)

urlpatterns = [
    path("admin/", admin.site.urls),
    # ======================
    # SWAGGER
    # ======================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # giao diện swagger
    path(
        "api/docs/elements/",
        SpectacularElementsView.as_view(),
        name="elements",
    ),
    # Các route của accounts
    # Đường dẫn đăng nhập để lấy Token (thay cho login_view cũ)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/", accounts_views.getAuth, name="current-user"),
    # Đường dẫn để lấy Access Token mới khi cái cũ hết hạn (Refresh Token)
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", accounts_views.register_view, name="register"),
    path("api/profile/", accounts_views.user_profile, name="user_profile"),
    path("api/wallet/", payment_views.wallet_summary, name="wallet_summary"),
    path(
        "api/wallet/coin-history/",
        payment_views.coin_histories,
        name="coin_histories",
    ),
    path(
        "api/wallet/payment-history/",
        payment_views.payment_histories,
        name="payment_histories",
    ),
    path(
        "api/wallet/topup/vnpay/",
        payment_views.vnpay_topup,
        name="vnpay_topup",
    ),
    path(
        "api/wallet/topup/vnpay/ipn/",
        payment_views.vnpay_ipn,
        name="vnpay_ipn",
    ),
    path(
        "api/wallet/topup/vnpay/result/",
        payment_views.vnpay_result,
        name="vnpay_result",
    ),
    # MoMo endpoints
    path(
        "api/wallet/topup/momo/",
        payment_views.momo_topup,
        name="momo_topup",
    ),
    path(
        "api/wallet/topup/momo/result/",
        payment_views.momo_result,
        name="momo_result",
    ),
    # Stripe endpoints
    path(
        "api/wallet/topup/stripe/",
        payment_views.stripe_topup,
        name="stripe_topup",
    ),
    path(
        "api/wallet/topup/stripe/webhook/",
        payment_views.stripe_webhook,
        name="stripe_webhook",
    ),
    # Các route của deck
    path("api/decks/", deck_views.user_decks, name="user_decks"),
    path("api/decks/public/", deck_views.public_decks, name="public_decks"),
    path(
        "api/decks/<int:deck_id>/learn/",
        deck_views.learn_public_deck,
        name="learn_public_deck",
    ),
    path(
        "api/decks/<int:deck_id>/unlearn/",
        deck_views.unlearn_deck,
        name="unlearn_deck",
    ),
    path("api/decks/move/", deck_views.move_user_deck, name="move_user_deck"),
    path(
        "api/decks/<int:deck_id>/",
        deck_views.user_deck_detail,
        name="user_deck_detail",
    ),
    path(
        "api/decks/<int:deck_id>/share/",
        deck_views.deck_share_settings,
        name="deck_share_settings",
    ),
    path(
        "api/decks/<int:deck_id>/collaborators/",
        deck_views.deck_add_collaborator,
        name="deck_add_collaborator",
    ),
    path(
        "api/decks/<int:deck_id>/collaborators/<int:user_id>/",
        deck_views.deck_remove_collaborator,
        name="deck_remove_collaborator",
    ),
    path("api/users/search/", deck_views.search_users, name="search_users"),
    path(
        "api/decks/<int:deck_id>/cards/",
        card_views.list_cards_by_deck,
        name="list_cards_by_deck",
    ),
    path(
        "api/decks/<int:deck_id>/study/",
        card_views.get_study_cards,
        name="get_study_cards",
    ),
    path(
        "api/cards/<int:card_id>/review/",
        card_views.review_card,
        name="review_card",
    ),
    path(
        "api/cards/<int:card_id>/",
        card_views.card_detail,
        name="card_detail",
    ),
    # Các route của note
    path("api/note-types/", note_views.note_types_view, name="note_types"),
    path(
        "api/decks/<int:deck_id>/notes/",
        note_views.create_note,
        name="create_note_by_deck",
    ),
]
