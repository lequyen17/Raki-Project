from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.deck.serializers import (
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
from apps.deck.services import DeckService


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
        serializer = DeckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = DeckService.create_deck(request.user, serializer.validated_data)
        return ApiResponse(data=data, message="Deck created successfully", status_code=201)

    data = DeckService.get_user_decks(request.user)
    return ApiResponse(data=data)


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
    serializer = DeckMoveSerializer(
        data=request.data, context={"user": request.user}
    )
    serializer.is_valid(raise_exception=True)
    data = DeckService.move_deck(request.user, serializer.validated_data)
    return ApiResponse(data=data, message="Deck moved successfully")


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
    if request.method == "GET":
        data = DeckService.get_deck_detail(deck_id, request.user)
        return ApiResponse(data=data)

    if request.method == "PUT":
        deck = DeckService._get_deck_for_owner_or_404(deck_id, request.user)
        serializer = DeckSerializer(data=request.data, context={"deck": deck})
        serializer.is_valid(raise_exception=True)
        data = DeckService.update_deck(deck, serializer.validated_data)
        return ApiResponse(data=data, message="Deck updated successfully")

    data = DeckService.delete_deck(deck_id, request.user)
    return ApiResponse(data=data, message="Deck deleted successfully")


@extend_schema(
    methods=["GET"],
    tags=["Decks"],
    summary="Danh sách deck cộng đồng (public)",
    responses={200: PublicDeckListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def public_decks(request):
    data = DeckService.get_public_decks(request.user)
    return ApiResponse(data=data)


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
    data = DeckService.learn_public_deck(deck_id, request.user)
    return ApiResponse(data=data, message="Deck learned successfully")


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
    data = DeckService.unlearn_deck(deck_id, request.user)
    return ApiResponse(data=data, message="Deck unlearned successfully")


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
    if request.method == "GET":
        data = DeckService.get_share_settings(deck_id, request.user)
        return ApiResponse(data=data)

    serializer = DeckShareSettingsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = DeckService.update_share_settings(
        deck_id, request.user, serializer.validated_data
    )
    return ApiResponse(data=data, message="Share settings updated successfully")


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
    serializer = DeckCollaboratorAddSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = DeckService.add_collaborator(
        deck_id, request.user, serializer.validated_data
    )
    return ApiResponse(data=data, message="Collaborator added successfully")


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
    data = DeckService.remove_collaborator(deck_id, request.user, user_id)
    return ApiResponse(data=data, message="Collaborator removed successfully")


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
    return ApiResponse(data=data)
