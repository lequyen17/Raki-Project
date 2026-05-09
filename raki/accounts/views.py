import json


from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from card.models import Card

User = get_user_model()


class MyTokenLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user

    # 1. Đếm số thẻ (Card)

    total_cards = Card.objects.filter(note__deck__deck_users__user=user).count()

    # 2. Lấy thông tin từ bảng Profile
    # Sử dụng try-except để an toàn tuyệt đối nếu user chưa có Profile
    try:
        profile = user.profile
        phone = profile.phone

        from card.models import Progress

        total_learned_cards = Progress.objects.filter(user=user).count()

        if profile.total_learned_cards != total_learned_cards:
            profile.total_learned_cards = total_learned_cards
            profile.save(update_fields=["total_learned_cards"])
    except AttributeError:
        # Nếu chưa có profile thì trả về giá trị mặc định
        phone = ""
        total_learned_cards = 0

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,  # Lấy từ bảng User
            "last_name": user.last_name,  # Lấy từ bảng User
            "phone": phone,  # Lấy từ bảng Profile
            "total_cards": total_cards,
            "total_learned_cards": total_learned_cards,
            "is_staff": user.is_staff,
            "groups": list(user.groups.values_list("name", flat=True)),
        }
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update user profile: email, first_name, last_name, phone
    Requires authentication via Bearer token
    """
    user = request.user

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=400)

    # Get fields from request (all optional)
    email = data.get("email", user.email).strip()
    first_name = data.get("first_name", user.first_name).strip()
    last_name = data.get("last_name", user.last_name).strip()
    phone = data.get("phone", user.profile.phone or "").strip()

    # Validate email format if provided
    if email != user.email:
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Email không hợp lệ"}, status=400)

        # Check if email already exists
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response({"error": "Email này đã được đăng ký"}, status=400)

    # Validate first_name and last_name length if provided
    if first_name and (len(first_name) < 2 or len(first_name) > 150):
        return Response({"error": "Tên đầu phải từ 2 đến 150 ký tự"}, status=400)

    if last_name and (len(last_name) < 2 or len(last_name) > 150):
        return Response({"error": "Họ phải từ 2 đến 150 ký tự"}, status=400)

    # Validate phone length if provided
    if phone and len(phone) > 15:
        return Response({"error": "Số điện thoại không hợp lệ"}, status=400)

    try:
        # Update user fields
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update profile phone
        user.profile.phone = phone
        user.profile.save()

        # Count total cards
        from card.models import Progress

        total_cards = Card.objects.filter(note__deck__deck_users__user=user).count()
        total_learned_cards = Progress.objects.filter(user=user).count()

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
    """
    Register a new user with username, password, email, first_name, last_name, phone
    Validates input and saves to User and Profile tables
    """
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

    # Validate all required fields
    if not all([username, password, confirm_password, email, first_name, last_name]):
        return JsonResponse(
            {"error": "Vui lòng điền đầy đủ tất cả các trường bắt buộc"}, status=400
        )

    # Validate username length and format
    if len(username) < 3:
        return JsonResponse(
            {"error": "Tên đăng nhập phải có ít nhất 3 ký tự"}, status=400
        )

    if len(username) > 150:
        return JsonResponse(
            {"error": "Tên đăng nhập không được vượt quá 150 ký tự"}, status=400
        )

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Tên đăng nhập đã tồn tại"}, status=400)

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Email không hợp lệ"}, status=400)

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email này đã được đăng ký"}, status=400)

    # Validate password
    if len(password) < 6:
        return JsonResponse({"error": "Mật khẩu phải có ít nhất 6 ký tự"}, status=400)

    # Check password confirmation
    if password != confirm_password:
        return JsonResponse({"error": "Mật khẩu xác nhận không khớp"}, status=400)

    # Validate first_name and last_name length
    if len(first_name) < 2 or len(first_name) > 150:
        return JsonResponse({"error": "Tên đầu phải từ 2 đến 150 ký tự"}, status=400)

    if len(last_name) < 2 or len(last_name) > 150:
        return JsonResponse({"error": "Họ phải từ 2 đến 150 ký tự"}, status=400)

    # Validate phone (if provided)
    if phone and len(phone) > 15:
        return JsonResponse({"error": "Số điện thoại không hợp lệ"}, status=400)

    try:
        # Create user with first_name and last_name
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Update profile with phone
        profile = user.profile
        profile.phone = phone
        profile.save()

        # Return success with user data
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
