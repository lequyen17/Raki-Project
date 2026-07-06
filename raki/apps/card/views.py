from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.card.serializers import (
    CardListResponseSerializer,
    ReviewCardResponseSerializer,
    ReviewCardSerializer,
    StudySessionResponseSerializer,
    CardDetailResponseSerializer,
    CardUpdateSerializer,
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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):
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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_study_cards(request, deck_id):
    data = CardMainService.get_study_cards(deck_id, request.user)
    return ApiResponse(data=data)


@extend_schema(
    tags=["Cards"],
    summary="Chấm điểm khi review thẻ",
    request=ReviewCardSerializer,
    responses={
        200: ReviewCardResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_card(request, card_id):
    serializer = ReviewCardSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = CardMainService.review_card(card_id, request.user, serializer.validated_data)
    return ApiResponse(data=data, message="Card reviewed successfully")


@extend_schema(
    methods=["GET"],
    tags=["Cards"],
    summary="Chi tiết thẻ",
    responses={
        200: CardDetailResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@extend_schema(
    methods=["PUT"],
    tags=["Cards"],
    summary="Cập nhật thẻ",
    request=CardUpdateSerializer,
    responses={
        200: CardDetailResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["Cards"],
    summary="Xóa thẻ",
    responses={
        200: {"type": "object", "properties": {"success": {"type": "boolean"}}},
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def card_detail(request, card_id):
    if request.method == "GET":
        data = CardMainService.get_card_detail(card_id, request.user)
        return ApiResponse(data=data)

    if request.method == "PUT":
        serializer = CardUpdateSerializer(
            data=request.data, context={"card_id": card_id, "user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = CardMainService.update_card(
            card_id, request.user, serializer.validated_data["field_values"]
        )
        return ApiResponse(data=data, message="Card updated successfully")

    data = CardMainService.delete_card(card_id, request.user)
    return ApiResponse(data=data, message="Card deleted successfully")
