from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.api_validation import parse_request
from config.openapi_common import ErrorResponseSerializer
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
        validated, error_response = parse_request(request, NoteTypeSerializer)
        if error_response:
            return error_response

        data = NoteMainService.create_note_type(request.user, validated)
        return Response(data, status=201)

    data = NoteMainService.get_note_types(request.user)
    return Response(data)


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
    validated, error_response = parse_request(
        request, NoteCreateSerializer, user=request.user
    )
    if error_response:
        return error_response

    try:
        data = NoteMainService.create_note(deck_id, request.user, validated)
        return Response(data, status=201)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
