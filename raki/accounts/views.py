from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from raki.api_validation import parse_request
from raki.openapi_common import ErrorResponseSerializer
from accounts.serializers import (
    CurrentUserSerializer,
    ProfileUpdateResponseSerializer,
    RegisterResponseSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
)
from accounts.services import UserService


@extend_schema(
    tags=["Accounts"],
    summary="Thông tin user đang đăng nhập",
    responses={200: CurrentUserSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAuth(request):
    return Response(
        {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }
    )


@extend_schema(
    methods=["GET"],
    tags=["Accounts"],
    summary="Lấy hồ sơ người dùng",
    responses={200: UserProfileSerializer},
)
@extend_schema(
    methods=["PUT"],
    tags=["Accounts"],
    summary="Cập nhật hồ sơ",
    request=UserProfileUpdateSerializer,
    responses={
        200: ProfileUpdateResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    if request.method == "GET":
        profile_data = UserService.get_user_profile_data(user)

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": profile_data["phone"],
                "total_cards": profile_data["total_cards"],
                "total_learned_cards": profile_data["total_learned_cards"],
                "is_staff": user.is_staff,
                "groups": list(user.groups.values_list("name", flat=True)),
            }
        )

    validated, error_response = parse_request(
        request, UserProfileUpdateSerializer, user=user
    )
    if error_response:
        return error_response

    try:
        data = UserService.update_user_profile(user, validated)
        return Response(data, status=200)
    except Exception as e:
        return Response({"error": f"Lỗi cập nhật hồ sơ: {str(e)}"}, status=500)


@extend_schema(
    tags=["Accounts"],
    summary="Đăng ký tài khoản",
    auth=[],
    request=UserRegistrationSerializer,
    responses={
        201: RegisterResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
def register_view(request):
    validated, error_response = parse_request(request, UserRegistrationSerializer)
    if error_response:
        return error_response

    try:
        data = UserService.register_user(validated)
        return Response(data, status=201)
    except Exception as e:
        return JsonResponse({"error": f"Lỗi đăng ký: {str(e)}"}, status=500)
