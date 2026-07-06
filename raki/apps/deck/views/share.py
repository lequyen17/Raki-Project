from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.deck.serializers import (
    DeckCollaboratorAddSerializer,
    DeckShareSettingsResponseSerializer,
    DeckShareSettingsSerializer,
)
from apps.deck.services import DeckService


@extend_schema_view(
    get=extend_schema(
        tags=["Decks"],
        summary="Lấy cài đặt chia sẻ deck",
        responses={
            200: DeckShareSettingsResponseSerializer,
            403: ErrorResponseSerializer,
        },
    ),
    put=extend_schema(
        tags=["Decks"],
        summary="Cập nhật cài đặt chia sẻ deck",
        request=DeckShareSettingsSerializer,
        responses={
            200: DeckShareSettingsResponseSerializer,
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    ),
)
class DeckShareSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, deck_id):
        data = DeckService.get_share_settings(deck_id, request.user)
        return ApiResponse(data=data)

    def put(self, request, deck_id):
        serializer = DeckShareSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = DeckService.update_share_settings(
            deck_id, request.user, serializer.validated_data
        )
        return ApiResponse(data=data, message="Share settings updated successfully")


@extend_schema(
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
class DeckAddCollaboratorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, deck_id):
        serializer = DeckCollaboratorAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = DeckService.add_collaborator(
            deck_id, request.user, serializer.validated_data
        )
        return ApiResponse(data=data, message="Collaborator added successfully")


@extend_schema(
    tags=["Decks"],
    summary="Xóa người được chia sẻ deck",
    responses={
        200: DeckShareSettingsResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
class DeckRemoveCollaboratorView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, deck_id, user_id):
        data = DeckService.remove_collaborator(deck_id, request.user, user_id)
        return ApiResponse(data=data, message="Collaborator removed successfully")
