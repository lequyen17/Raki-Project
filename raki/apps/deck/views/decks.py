from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.deck.serializers import (
    DeckItemSerializer,
    DeckListResponseSerializer,
    DeckMoveResponseSerializer,
    DeckMoveSerializer,
    DeckSerializer,
)
from apps.deck.services import DeckService


@extend_schema_view(
    get=extend_schema(
        tags=["Decks"],
        operation_id="decks_list",
        summary="Danh sách deck của user",
        responses={200: DeckListResponseSerializer},
    ),
    post=extend_schema(
        tags=["Decks"],
        summary="Tạo deck mới",
        request=DeckSerializer,
        responses={
            201: DeckItemSerializer,
            400: ErrorResponseSerializer,
        },
    ),
)
class UserDecksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DeckService.get_user_decks(request.user)
        return ApiResponse(data=data)

    def post(self, request):
        serializer = DeckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = DeckService.create_deck(request.user, serializer.validated_data)
        return ApiResponse(data=data, message="Deck created successfully", status_code=201)


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
class MoveUserDeckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeckMoveSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = DeckService.move_deck(request.user, serializer.validated_data)
        return ApiResponse(data=data, message="Deck moved successfully")
