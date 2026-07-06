from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.deck.serializers import (
    PublicDeckListResponseSerializer,
    SuccessResponseSerializer,
)
from apps.deck.services import DeckService


@extend_schema(
    tags=["Decks"],
    summary="Danh sách deck cộng đồng (public)",
    responses={200: PublicDeckListResponseSerializer},
)
class PublicDecksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DeckService.get_public_decks(request.user)
        return ApiResponse(data=data)


@extend_schema(
    tags=["Decks"],
    summary="Học một deck công khai",
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
class LearnPublicDeckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, deck_id):
        data = DeckService.learn_public_deck(deck_id, request.user)
        return ApiResponse(data=data, message="Deck learned successfully")


@extend_schema(
    tags=["Decks"],
    summary="Bỏ học deck cộng đồng (xóa role viewer)",
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
class UnlearnDeckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, deck_id):
        data = DeckService.unlearn_deck(deck_id, request.user)
        return ApiResponse(data=data, message="Deck unlearned successfully")
