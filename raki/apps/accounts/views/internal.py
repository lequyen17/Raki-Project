from django.conf import settings as django_settings
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from core.exceptions.exceptions import UnauthorizedException
from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.accounts.serializers import (
    BatchUsersResponseSerializer,
    DueUsersResponseSerializer,
)
from apps.accounts.services import UserService


@extend_schema(
    tags=["Internal"],
    summary="[Internal] Danh sách users có thẻ cần ôn tập",
    description=(
        "API nội bộ dành cho mail service. "
        "Yêu cầu header `X-Internal-Token` khớp với `INTERNAL_API_TOKEN` trong settings."
    ),
    responses={
        200: DueUsersResponseSerializer,
        401: ErrorResponseSerializer,
    },
)
class UsersWithDueCardsView(APIView):
    def get(self, request):
        """
        Trả về danh sách users có ít nhất 1 card với next_review <= hôm nay.
        Chỉ cho phép gọi từ internal service (xác thực bằng X-Internal-Token).
        """
        token = request.headers.get("X-Internal-Token", "")
        if token != django_settings.INTERNAL_API_TOKEN:
            raise UnauthorizedException("UNAUTHORIZED")

        users = UserService.get_users_with_due_cards()
        return ApiResponse(data={"users": users})


@extend_schema(
    tags=["Internal"],
    summary="[Internal] Lấy thông tin users theo danh sách ID",
    description=(
        "API nội bộ dành cho chat service. "
        "Yêu cầu header `X-Internal-Token` khớp với `INTERNAL_API_TOKEN` trong settings."
    ),
    responses={
        200: BatchUsersResponseSerializer,
        401: ErrorResponseSerializer,
    },
)
class UsersBatchView(APIView):
    def get(self, request):
        token = request.headers.get("X-Internal-Token", "")
        if token != django_settings.INTERNAL_API_TOKEN:
            raise UnauthorizedException("UNAUTHORIZED")

        ids_param = request.query_params.get("ids", "")
        user_ids = []
        for part in ids_param.split(","):
            part = part.strip()
            if part.isdigit():
                user_ids.append(int(part))

        users = UserService.get_users_by_ids(user_ids)
        return ApiResponse(data={"users": users})
