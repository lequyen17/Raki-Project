from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.card.serializers import (
    CardListResponseSerializer,
    StudySessionResponseSerializer,
)
from apps.card.services.main_service import CardMainService


@extend_schema(
    tags=["Cards"],
    summary="Danh sách thẻ theo deck",
    responses={
        200: CardListResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
class ListCardsByDeckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, deck_id):
        data = CardMainService.list_cards_by_deck(deck_id, request.user)
        return ApiResponse(data=data)


@extend_schema(
    tags=["Cards"],
    summary="Lấy thẻ để học (study session)",
    responses={
        200: StudySessionResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
class StudyCardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, deck_id):
        data = CardMainService.get_study_cards(deck_id, request.user)
        return ApiResponse(data=data)
