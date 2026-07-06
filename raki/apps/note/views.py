from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.note.serializers import (
    NoteCreateResponseSerializer,
    NoteCreateSerializer,
    NoteTypeCreateResponseSerializer,
    NoteTypeListResponseSerializer,
    NoteTypeSerializer,
)
from apps.note.services.main_service import NoteMainService


@extend_schema(
    methods=["GET"],
    tags=["Notes"],
    summary="Danh sách note type",
    responses={200: NoteTypeListResponseSerializer},
)
@extend_schema(
    methods=["POST"],
    tags=["Notes"],
    summary="Tạo note type",
    request=NoteTypeSerializer,
    responses={
        201: NoteTypeCreateResponseSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def note_types_view(request):
    if request.method == "POST":
        serializer = NoteTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = NoteMainService.create_note_type(request.user, serializer.validated_data)
        return ApiResponse(data=data, message="Note type created successfully", status_code=201)

    data = NoteMainService.get_note_types(request.user)
    return ApiResponse(data=data)


@extend_schema(
    tags=["Notes"],
    summary="Tạo note trong deck",
    request=NoteCreateSerializer,
    responses={
        201: NoteCreateResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_note(request, deck_id):
    serializer = NoteCreateSerializer(
        data=request.data, context={"user": request.user}
    )
    serializer.is_valid(raise_exception=True)
    data = NoteMainService.create_note(
        deck_id, request.user, serializer.validated_data
    )
    return ApiResponse(data=data, message="Note created successfully", status_code=201)
