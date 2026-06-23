from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.api_validation import parse_request
from config.openapi_common import ErrorResponseSerializer
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
    try:
        data = CardMainService.list_cards_by_deck(deck_id, request.user)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


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
    try:
        data = CardMainService.get_study_cards(deck_id, request.user)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


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
    validated, error_response = parse_request(request, ReviewCardSerializer)
    if error_response:
        return error_response

    try:
        data = CardMainService.review_card(card_id, request.user, validated)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


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
        try:
            data = CardMainService.get_card_detail(card_id, request.user)
            return Response(data)
        except LookupError as e:
            return Response({"error": str(e)}, status=404)

    elif request.method == "PUT":
        validated, error_response = parse_request(
            request, CardUpdateSerializer, card_id=card_id, user=request.user
        )
        if error_response:
            return error_response

        try:
            data = CardMainService.update_card(
                card_id, request.user, validated["field_values"]
            )
            return Response(data)
        except LookupError as e:
            return Response({"error": str(e)}, status=404)

    elif request.method == "DELETE":
        try:
            data = CardMainService.delete_card(card_id, request.user)
            return Response(data)
        except LookupError as e:
            return Response({"error": str(e)}, status=404)
