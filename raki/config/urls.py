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

from django.http import JsonResponse
from django.contrib import admin
from django.urls import path


def health_check(request):
    return JsonResponse({"status": "ok"})


from apps.accounts import views as accounts_views
from apps.deck import views as deck_views
from apps.card import views as card_views
from apps.note import views as note_views
from apps.payment import views as payment_views
# Payment serializers — views handle their own imports via extend_schema
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
    path("health/", health_check, name="health_check"),
    path("api/health/", health_check, name="api_health_check"),
    path("api/admin/", admin.site.urls),
    # ======================
    # SWAGGER
    # ======================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/elements/",
        SpectacularElementsView.as_view(),
        name="elements",
    ),
    # Các route của accounts
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/auth/",
        accounts_views.CurrentUserView.as_view(),
        name="current-user",
    ),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "api/register/",
        accounts_views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "api/register/verify-otp/",
        accounts_views.VerifyOtpView.as_view(),
        name="register_verify_otp",
    ),
    path(
        "api/profile/",
        accounts_views.UserProfileView.as_view(),
        name="user_profile",
    ),
    path(
        "api/profile/avatar/",
        accounts_views.ProfileAvatarUploadView.as_view(),
        name="user_profile_avatar",
    ),
    path(
        "api/wallet/",
        payment_views.WalletSummaryView.as_view(),
        name="wallet_summary",
    ),
    path(
        "api/wallet/coin-history/",
        payment_views.CoinHistoriesView.as_view(),
        name="coin_histories",
    ),
    path(
        "api/wallet/payment-history/",
        payment_views.PaymentHistoriesView.as_view(),
        name="payment_histories",
    ),
    path(
        "api/wallet/topup/vnpay/",
        payment_views.VnpayTopupView.as_view(),
        name="vnpay_topup",
    ),
    path(
        "api/wallet/topup/vnpay/ipn/",
        payment_views.VnpayIpnView.as_view(),
        name="vnpay_ipn",
    ),
    path(
        "api/wallet/topup/vnpay/result/",
        payment_views.VnpayResultView.as_view(),
        name="vnpay_result",
    ),
    path(
        "api/wallet/topup/momo/",
        payment_views.MomoTopupView.as_view(),
        name="momo_topup",
    ),
    path(
        "api/wallet/topup/momo/result/",
        payment_views.MomoResultView.as_view(),
        name="momo_result",
    ),
    path(
        "api/wallet/topup/stripe/",
        payment_views.StripeTopupView.as_view(),
        name="stripe_topup",
    ),
    path(
        "api/wallet/topup/stripe/webhook/",
        payment_views.StripeWebhookView.as_view(),
        name="stripe_webhook",
    ),
    # Các route của deck
    path(
        "api/decks/",
        deck_views.UserDecksView.as_view(),
        name="user_decks",
    ),
    path(
        "api/decks/public/",
        deck_views.PublicDecksView.as_view(),
        name="public_decks",
    ),
    path(
        "api/decks/<int:deck_id>/learn/",
        deck_views.LearnPublicDeckView.as_view(),
        name="learn_public_deck",
    ),
    path(
        "api/decks/<int:deck_id>/unlearn/",
        deck_views.UnlearnDeckView.as_view(),
        name="unlearn_deck",
    ),
    path(
        "api/decks/move/",
        deck_views.MoveUserDeckView.as_view(),
        name="move_user_deck",
    ),
    path(
        "api/decks/<int:deck_id>/",
        deck_views.UserDeckDetailView.as_view(),
        name="user_deck_detail",
    ),
    path(
        "api/decks/<int:deck_id>/share/",
        deck_views.DeckShareSettingsView.as_view(),
        name="deck_share_settings",
    ),
    path(
        "api/decks/<int:deck_id>/collaborators/",
        deck_views.DeckAddCollaboratorView.as_view(),
        name="deck_add_collaborator",
    ),
    path(
        "api/decks/<int:deck_id>/collaborators/<int:user_id>/",
        deck_views.DeckRemoveCollaboratorView.as_view(),
        name="deck_remove_collaborator",
    ),
    path(
        "api/users/search/",
        deck_views.SearchUsersView.as_view(),
        name="search_users",
    ),
    path(
        "api/decks/<int:deck_id>/cards/",
        card_views.ListCardsByDeckView.as_view(),
        name="list_cards_by_deck",
    ),
    path(
        "api/decks/<int:deck_id>/study/",
        card_views.StudyCardsView.as_view(),
        name="get_study_cards",
    ),
    path(
        "api/cards/<int:card_id>/review/",
        card_views.ReviewCardView.as_view(),
        name="review_card",
    ),
    path(
        "api/cards/<int:card_id>/",
        card_views.CardDetailView.as_view(),
        name="card_detail",
    ),
    # Các route của note
    path(
        "api/note-types/",
        note_views.NoteTypesView.as_view(),
        name="note_types",
    ),
    path(
        "api/decks/<int:deck_id>/notes/",
        note_views.CreateNoteView.as_view(),
        name="create_note_by_deck",
    ),
    # Internal API — dành cho mail service
    path(
        "api/users/review-due/",
        accounts_views.UsersWithDueCardsView.as_view(),
        name="users_review_due",
    ),
    path(
        "api/users/batch/",
        accounts_views.UsersBatchView.as_view(),
        name="users_batch",
    ),
]
