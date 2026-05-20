from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from raki.api_validation import parse_request
from raki.openapi_common import ErrorResponseSerializer
from card.serializers import (
    CardListResponseSerializer,
    ReviewCardResponseSerializer,
    ReviewCardSerializer,
    StudySessionResponseSerializer,
)
from card.services.main_service import CardMainService


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
