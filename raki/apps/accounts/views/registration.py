from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.accounts.serializers import (
    OtpVerifySerializer,
    RegisterResponseSerializer,
    UserRegistrationSerializer,
)
from apps.accounts.services import UserService


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
class RegisterView(APIView):
    def post(self, request):
        """
        Bước 1: Nhận thông tin đăng ký, validate, tạo OTP, lưu Redis (5 phút),
        gửi OTP qua email. Chưa tạo tài khoản.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = UserService.initiate_registration(serializer.validated_data)
        return ApiResponse(data=data, message="OTP sent successfully")


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
class VerifyOtpView(APIView):
    def post(self, request):
        """
        Bước 2: Nhận email + OTP, xác thực với Redis.
        Nếu đúng thì tạo tài khoản và gửi mail chào mừng.
        """
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        data = UserService.verify_otp_and_register(email, otp)
        return ApiResponse(data=data, message="Registered successfully", status_code=201)
