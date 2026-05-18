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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):

    user = request.user

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
            ":username": user.username,
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


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):

    user = request.user

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:

        return Response({"error": "Invalid JSON"}, status=400)

    email = data.get("email", user.email).strip()

    first_name = data.get("first_name", user.first_name).strip()

    last_name = data.get("last_name", user.last_name).strip()

    phone = data.get("phone", user.profile.phone or "").strip()

    # Validate email
    if email != user.email:

        try:
            validate_email(email)

        except ValidationError:

            return Response({"error": "Email không hợp lệ"}, status=400)

        if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():

            return Response({"error": "Email này đã được đăng ký"}, status=400)

    # Validate first_name
    if first_name and (len(first_name) < 2 or len(first_name) > 150):

        return Response({"error": "Tên đầu phải từ 2 đến 150 ký tự"}, status=400)

    # Validate last_name
    if last_name and (len(last_name) < 2 or len(last_name) > 150):

        return Response({"error": "Họ phải từ 2 đến 150 ký tự"}, status=400)

    # Validate phone
    if phone and len(phone) > 15:

        return Response({"error": "Số điện thoại không hợp lệ"}, status=400)

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

        return Response({"error": f"Lỗi cập nhật hồ sơ: {str(e)}"}, status=500)


@api_view(["POST"])
def register_view(request):

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:

        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username", "").strip()

    password = data.get("password", "").strip()

    confirm_password = data.get("confirm_password", "").strip()

    email = data.get("email", "").strip()

    first_name = data.get("first_name", "").strip()

    last_name = data.get("last_name", "").strip()

    phone = data.get("phone", "").strip()

    # Validate required fields
    if not all(
        [
            username,
            password,
            confirm_password,
            email,
            first_name,
            last_name,
        ]
    ):

        return JsonResponse(
            {"error": "Vui lòng điền đầy đủ tất cả các trường bắt buộc"}, status=400
        )

    # Validate username
    if len(username) < 3:

        return JsonResponse(
            {"error": "Tên đăng nhập phải có ít nhất 3 ký tự"}, status=400
        )

    if len(username) > 150:

        return JsonResponse(
            {"error": "Tên đăng nhập không được vượt quá 150 ký tự"}, status=400
        )

    if UserRepository.get_user_by_username(username).exists():

        return JsonResponse({"error": "Tên đăng nhập đã tồn tại"}, status=400)

    # Validate email
    try:
        validate_email(email)

    except ValidationError:

        return JsonResponse({"error": "Email không hợp lệ"}, status=400)

    if UserRepository.get_user_by_email(email).exists():

        return JsonResponse({"error": "Email này đã được đăng ký"}, status=400)

    # Validate password
    if len(password) < 6:

        return JsonResponse({"error": "Mật khẩu phải có ít nhất 6 ký tự"}, status=400)

    if password != confirm_password:

        return JsonResponse({"error": "Mật khẩu xác nhận không khớp"}, status=400)

    # Validate names
    if len(first_name) < 2 or len(first_name) > 150:

        return JsonResponse({"error": "Tên đầu phải từ 2 đến 150 ký tự"}, status=400)

    if len(last_name) < 2 or len(last_name) > 150:

        return JsonResponse({"error": "Họ phải từ 2 đến 150 ký tự"}, status=400)

    # Validate phone
    if phone and len(phone) > 15:

        return JsonResponse({"error": "Số điện thoại không hợp lệ"}, status=400)

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
