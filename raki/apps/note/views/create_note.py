from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.note.serializers import NoteCreateResponseSerializer, NoteCreateSerializer
from apps.note.services.main_service import NoteMainService


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
class CreateNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, deck_id):
        serializer = NoteCreateSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = NoteMainService.create_note(
            deck_id, request.user, serializer.validated_data
        )
        return ApiResponse(data=data, message="Note created successfully", status_code=201)
