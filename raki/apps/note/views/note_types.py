from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.note.serializers import (
    NoteTypeCreateResponseSerializer,
    NoteTypeListResponseSerializer,
    NoteTypeSerializer,
)
from apps.note.services.main_service import NoteMainService


@extend_schema_view(
    get=extend_schema(
        tags=["Notes"],
        summary="Danh sách note type",
        responses={200: NoteTypeListResponseSerializer},
    ),
    post=extend_schema(
        tags=["Notes"],
        summary="Tạo note type",
        request=NoteTypeSerializer,
        responses={
            201: NoteTypeCreateResponseSerializer,
            400: ErrorResponseSerializer,
        },
    ),
)
class NoteTypesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = NoteMainService.get_note_types(request.user)
        return ApiResponse(data=data)

    def post(self, request):
        serializer = NoteTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = NoteMainService.create_note_type(request.user, serializer.validated_data)
        return ApiResponse(
            data=data, message="Note type created successfully", status_code=201
        )
