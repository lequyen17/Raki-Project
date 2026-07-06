from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.accounts.serializers import (
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
