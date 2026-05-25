from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from raki.api_validation import parse_request
from raki.openapi_common import ErrorResponseSerializer
from deck.repositories import DeckRepository
from deck.serializers import (
    DeckDetailResponseSerializer,
    DeckItemSerializer,
    DeckListResponseSerializer,
    DeckMoveResponseSerializer,
    DeckMoveSerializer,
    DeckSerializer,
    SuccessResponseSerializer,
)
from deck.services import DeckService


@extend_schema(
    methods=["GET"],
    tags=["Decks"],
    operation_id="decks_list",
    summary="Danh sách deck của user",
    responses={200: DeckListResponseSerializer},
)
@extend_schema(
    methods=["POST"],
    tags=["Decks"],
    summary="Tạo deck mới",
    request=DeckSerializer,
    responses={
        201: DeckItemSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_decks(request):
    if request.method == "POST":
        validated, error_response = parse_request(request, DeckSerializer)
        if error_response:
            return error_response

        data = DeckService.create_deck(request.user, validated)
        return Response(data, status=201)

    data = DeckService.get_user_decks(request.user)
    return Response(data)


@extend_schema(
    tags=["Decks"],
    summary="Di chuyển deck (đổi parent)",
    request=DeckMoveSerializer,
    responses={
        200: DeckMoveResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_user_deck(request):
    validated, error_response = parse_request(
        request, DeckMoveSerializer, user=request.user
    )
    if error_response:
        return error_response

    data = DeckService.move_deck(validated)
    return Response(data)


@extend_schema(
    methods=["GET"],
    tags=["Decks"],
    summary="Chi tiết deck (thông tin + thống kê)",
    responses={
        200: DeckDetailResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@extend_schema(
    methods=["PUT"],
    tags=["Decks"],
    summary="Cập nhật deck",
    request=DeckSerializer,
    responses={
        200: DeckItemSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["Decks"],
    summary="Xóa deck",
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_deck_detail(request, deck_id):
    try:
        if request.method == "GET":
            data = DeckService.get_deck_detail(deck_id, request.user)
            return Response(data)
        elif request.method == "PUT":
            deck = DeckRepository.get_deck_for_user(deck_id, request.user)
            if not deck:
                return Response({"error": "DECK_NOT_FOUND"}, status=404)

            validated, error_response = parse_request(
                request, DeckSerializer, deck=deck
            )
            if error_response:
                return error_response

            data = DeckService.update_deck(deck, validated)
            return Response(data)
        elif request.method == "DELETE":
            data = DeckService.delete_deck(deck_id, request.user)
            return Response(data)

    except LookupError as e:
        return Response({"error": str(e)}, status=404)

