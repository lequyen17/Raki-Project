from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.deck.serializers import (
    DeckDetailResponseSerializer,
    DeckItemSerializer,
    DeckSerializer,
    SuccessResponseSerializer,
)
from apps.deck.services import DeckService


@extend_schema_view(
    get=extend_schema(
        tags=["Decks"],
        summary="Chi tiết deck (thông tin + thống kê)",
        responses={
            200: DeckDetailResponseSerializer,
            404: ErrorResponseSerializer,
        },
    ),
    put=extend_schema(
        tags=["Decks"],
        summary="Cập nhật deck",
        request=DeckSerializer,
        responses={
            200: DeckItemSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    ),
    delete=extend_schema(
        tags=["Decks"],
        summary="Xóa deck",
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
        },
    ),
)
class UserDeckDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, deck_id):
        data = DeckService.get_deck_detail(deck_id, request.user)
        return ApiResponse(data=data)

    def put(self, request, deck_id):
        deck = DeckService._get_deck_for_owner_or_404(deck_id, request.user)
        serializer = DeckSerializer(data=request.data, context={"deck": deck})
        serializer.is_valid(raise_exception=True)
        data = DeckService.update_deck(deck, serializer.validated_data)
        return ApiResponse(data=data, message="Deck updated successfully")

    def delete(self, request, deck_id):
        data = DeckService.delete_deck(deck_id, request.user)
        return ApiResponse(data=data, message="Deck deleted successfully")
