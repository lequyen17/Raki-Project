import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .repositories import UserRepository
from .serializers import UserProfileUpdateSerializer, UserRegistrationSerializer

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

        total_cards = UserRepository.count_total_cards(user)

        try:
            profile = user.profile

            total_learned_cards = UserRepository.count_total_learned_cards(user)

            if profile.total_learned_cards != total_learned_cards:
                profile.total_learned_cards = total_learned_cards
                profile.save(update_fields=["total_learned_cards"])

            phone = profile.phone

        except AttributeError:

            phone = ""
            total_learned_cards = 0

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": phone,
                "total_cards": total_cards,
                "total_learned_cards": total_learned_cards,
                "is_staff": user.is_staff,
                "groups": list(user.groups.values_list("name", flat=True)),
            }
        )

    # =========================
    # UPDATE PROFILE
    # =========================
    elif request.method == "PUT":

        try:
            data = json.loads(request.body)

        except json.JSONDecodeError:

            return Response({"error": "Invalid JSON"}, status=400)

        serializer = UserProfileUpdateSerializer(data=data, user=user)
        if not serializer.is_valid():
            return Response({"error": serializer.errors['non_field_errors'][0]}, status=400)
            
        validated_data = serializer.validated_data
        email = validated_data["email"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        phone = validated_data["phone"]

        try:

            # Update user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name

            user.save()

            # Update profile
            user.profile.phone = phone
            user.profile.save()

            total_cards = UserRepository.count_total_cards(user)

            total_learned_cards = UserRepository.count_total_learned_cards(user)

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
                        "phone": user.profile.phone,
                        "total_cards": total_cards,
                        "total_learned_cards": total_learned_cards,
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
        data = json.loads(request.body)

    except json.JSONDecodeError:

        return JsonResponse({"error": "Invalid JSON"}, status=400)

    serializer = UserRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"error": serializer.errors['non_field_errors'][0]}, status=400)
        
    validated_data = serializer.validated_data
    username = validated_data["username"]
    password = validated_data["password"]
    email = validated_data["email"]
    first_name = validated_data["first_name"]
    last_name = validated_data["last_name"]
    phone = validated_data["phone"]

    try:

        user = UserRepository.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        profile = user.profile
        profile.phone = phone
        profile.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Đăng ký thành công!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": profile.phone,
                },
            },
            status=201,
        )

    except Exception as e:

        return JsonResponse({"error": f"Lỗi đăng ký: {str(e)}"}, status=500)
