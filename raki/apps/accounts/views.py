from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.utils.api_validation import parse_request
from core.utils.openapi_common import ErrorResponseSerializer
from apps.accounts.serializers import (
    BatchUsersResponseSerializer,
    CurrentUserSerializer,
    DueUsersResponseSerializer,
    OtpVerifySerializer,
    ProfileUpdateResponseSerializer,
    RegisterResponseSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
)
from apps.accounts.services import UserService


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
            "id": request.user.id,
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
        return Response({"error": "PROFILE_UPDATE_FAILED"}, status=500)


@extend_schema(
    tags=["Accounts"],
    summary="Bước 1 đăng ký — Gửi OTP qua email",
    auth=[],
    request=UserRegistrationSerializer,
    responses={
        200: {"description": "OTP đã được gửi tới email"},
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
def register_view(request):
    """
    Bước 1: Nhận thông tin đăng ký, validate, tạo OTP, lưu Redis (5 phút),
    gửi OTP qua email. Chưa tạo tài khoản.
    """
    validated, error_response = parse_request(request, UserRegistrationSerializer)
    if error_response:
        return error_response

    try:
        data = UserService.initiate_registration(validated)
        return Response(data, status=200)
    except Exception as e:
        return JsonResponse({"error": "REGISTER_FAILED"}, status=500)


@extend_schema(
    tags=["Accounts"],
    summary="Bước 2 đăng ký — Xác thực OTP & tạo tài khoản",
    auth=[],
    request=OtpVerifySerializer,
    responses={
        201: RegisterResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
def verify_otp_view(request):
    """
    Bước 2: Nhận email + OTP, xác thực với Redis.
    Nếu đúng thì tạo tài khoản và gửi mail chào mừng.
    """
    validated, error_response = parse_request(request, OtpVerifySerializer)
    if error_response:
        return error_response

    email = validated["email"]
    otp = validated["otp"]

    try:
        data = UserService.verify_otp_and_register(email, otp)
        return Response(data, status=201)
    except ValueError as e:
        error_code = str(e)
        return JsonResponse({"error": error_code}, status=400)
    except Exception as e:
        return JsonResponse({"error": "REGISTER_FAILED"}, status=500)


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
@api_view(["GET"])
def users_with_due_cards(request):
    """
    Trả về danh sách users có ít nhất 1 card với next_review <= hôm nay.
    Chỉ cho phép gọi từ internal service (xác thực bằng X-Internal-Token).
    """
    from django.conf import settings as django_settings
    token = request.headers.get("X-Internal-Token", "")
    if token != django_settings.INTERNAL_API_TOKEN:
        return JsonResponse({"error": "UNAUTHORIZED"}, status=401)

    users = UserService.get_users_with_due_cards()
    return Response({"users": users}, status=200)


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
@api_view(["GET"])
def users_batch(request):
    from django.conf import settings as django_settings

    token = request.headers.get("X-Internal-Token", "")
    if token != django_settings.INTERNAL_API_TOKEN:
        return JsonResponse({"error": "UNAUTHORIZED"}, status=401)

    ids_param = request.query_params.get("ids", "")
    user_ids = []
    for part in ids_param.split(","):
        part = part.strip()
        if part.isdigit():
            user_ids.append(int(part))

    users = UserService.get_users_by_ids(user_ids)
    return Response({"users": users}, status=200)
