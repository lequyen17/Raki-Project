import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.services import UserService

from .serializers import UserProfileValidator, UserRegistrationValidator

User = get_user_model()


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


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):

    user = request.user

    # =========================
    # GET PROFILE
    # =========================
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

    # =========================
    # UPDATE PROFILE
    # =========================
    elif request.method == "PUT":

        try:
            validated_data = UserProfileValidator.validate_update(
                data=data,
                user=user,
            )
            result = UserService.update_user_profile(user, validated_data)

            return Response(
                {
                    "success": True,
                    "message": "Cập nhật hồ sơ thành công!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone": result["phone"],
                        "total_cards": result["total_cards"],
                        "total_learned_cards": result["total_learned_cards"],
                    },
                },
                status=200,
            )

        except Exception as e:

            return Response(
                {"error": f"Lỗi cập nhật hồ sơ: {str(e)}"},
                status=500,
            )


@api_view(["POST"])
def register_view(request):

    try:
        validated_data = UserRegistrationValidator.validate(request.data)
        user = UserService.register_user(validated_data)

        return Response(
            {
                "success": True,
                "message": "Đăng ký thành công!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=201,
        )

    except Exception as e:

        return JsonResponse({"error": f"Lỗi đăng ký: {str(e)}"}, status=500)
