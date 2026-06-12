from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from raki.api_validation import parse_request
from raki.openapi_common import ErrorResponseSerializer
from deck.repositories import DeckRepository
from deck.serializers import (
    DeckCollaboratorAddSerializer,
    DeckDetailResponseSerializer,
    DeckItemSerializer,
    DeckListResponseSerializer,
    DeckMoveResponseSerializer,
    DeckMoveSerializer,
    DeckSerializer,
    DeckShareSettingsResponseSerializer,
    DeckShareSettingsSerializer,
    SuccessResponseSerializer,
    PublicDeckListResponseSerializer,
    UserSearchResponseSerializer,
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

    deck = DeckRepository.get_deck_for_owner(validated["deck"].id, request.user)
    if not deck:
        return Response({"error": "DECK_NOT_FOUND_OR_NOT_OWNER"}, status=403)

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
            deck = DeckRepository.get_deck_for_owner(deck_id, request.user)
            if not deck:
                return Response({"error": "DECK_NOT_FOUND_OR_NOT_OWNER"}, status=403)

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


@extend_schema(
    methods=["GET"],
    tags=["Decks"],
    summary="Danh sách deck cộng đồng (public)",
    responses={200: PublicDeckListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def public_decks(request):
    data = DeckService.get_public_decks()
    return Response(data)


@extend_schema(
    methods=["POST"],
    tags=["Decks"],
    summary="Học một deck công khai",
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def learn_public_deck(request, deck_id):
    try:
        data = DeckService.learn_public_deck(deck_id, request.user)

        if isinstance(data, dict) and data.get("success") is False:
            status = 402 if data.get("error") == "INSUFFICIENT_COINS" else 400
            return Response(data, status=status)

        return Response(data, status=200)

    except LookupError as e:
        return Response({"error": str(e)}, status=404)


@extend_schema(
    methods=["POST"],
    tags=["Decks"],
    summary="Bỏ học deck cộng đồng (xóa role viewer)",
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unlearn_deck(request, deck_id):
    try:
        data = DeckService.unlearn_deck(deck_id, request.user)
        return Response(data, status=200)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


@extend_schema(
    methods=["GET"],
    tags=["Decks"],
    summary="Lấy cài đặt chia sẻ deck",
    responses={
        200: DeckShareSettingsResponseSerializer,
        403: ErrorResponseSerializer,
    },
)
@extend_schema(
    methods=["PUT"],
    tags=["Decks"],
    summary="Cập nhật cài đặt chia sẻ deck",
    request=DeckShareSettingsSerializer,
    responses={
        200: DeckShareSettingsResponseSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def deck_share_settings(request, deck_id):
    try:
        if request.method == "GET":
            data = DeckService.get_share_settings(deck_id, request.user)
            return Response(data)

        validated, error_response = parse_request(request, DeckShareSettingsSerializer)
        if error_response:
            return error_response

        data = DeckService.update_share_settings(deck_id, request.user, validated)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=403)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)


@extend_schema(
    methods=["POST"],
    tags=["Decks"],
    summary="Thêm người được chia sẻ deck",
    request=DeckCollaboratorAddSerializer,
    responses={
        200: DeckShareSettingsResponseSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deck_add_collaborator(request, deck_id):
    try:
        validated, error_response = parse_request(
            request, DeckCollaboratorAddSerializer
        )
        if error_response:
            return error_response

        data = DeckService.add_collaborator(deck_id, request.user, validated)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)


@extend_schema(
    methods=["DELETE"],
    tags=["Decks"],
    summary="Xóa người được chia sẻ deck",
    responses={
        200: DeckShareSettingsResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deck_remove_collaborator(request, deck_id, user_id):
    try:
        data = DeckService.remove_collaborator(deck_id, request.user, user_id)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


@extend_schema(
    methods=["GET"],
    tags=["Decks"],
    summary="Tìm kiếm user theo username",
    responses={200: UserSearchResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.query_params.get("q", "")
    data = DeckService.search_users(query, request.user)
    return Response(data)
