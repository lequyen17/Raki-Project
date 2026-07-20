from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.exceptions.exceptions import BadRequestException
from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.accounts.serializers import (
    AvatarUploadResponseSerializer,
    ProfileUpdateResponseSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)
from apps.accounts.services import UserService


@extend_schema_view(
    get=extend_schema(
        tags=["Accounts"],
        summary="Lấy hồ sơ người dùng",
        responses={200: UserProfileSerializer},
    ),
    put=extend_schema(
        tags=["Accounts"],
        summary="Cập nhật hồ sơ",
        request=UserProfileUpdateSerializer,
        responses={
            200: ProfileUpdateResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    ),
)
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_data = UserService.get_user_profile_data(user)
        return ApiResponse(
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": profile_data["phone"],
                "avatar": profile_data.get("avatar"),
                "total_cards": profile_data["total_cards"],
                "total_learned_cards": profile_data["total_learned_cards"],
                "is_staff": user.is_staff,
            }
        )

    def put(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(
            data=request.data, context={"user": user}
        )
        serializer.is_valid(raise_exception=True)
        data = UserService.update_user_profile(user, serializer.validated_data)
        return ApiResponse(data=data, message="Profile updated successfully")


@extend_schema(
    tags=["Accounts"],
    summary="Upload avatar hồ sơ lên Cloudflare R2",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "avatar": {"type": "string", "format": "binary"},
            },
            "required": ["avatar"],
        }
    },
    responses={
        200: AvatarUploadResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
class ProfileAvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        uploaded = request.FILES.get("avatar")
        if not uploaded:
            raise BadRequestException("AVATAR_REQUIRED")

        data = UserService.upload_user_avatar(request.user, uploaded)
        return ApiResponse(data=data, message="Avatar uploaded successfully")
