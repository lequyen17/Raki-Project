from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import CurrentUserSerializer


@extend_schema(
    tags=["Accounts"],
    summary="Thông tin user đang đăng nhập",
    responses={200: CurrentUserSerializer},
)
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        avatar = None
        try:
            avatar = request.user.profile.avatar
        except Exception:
            avatar = None

        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "avatar": avatar,
            }
        )
