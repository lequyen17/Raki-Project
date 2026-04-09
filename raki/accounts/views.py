from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user) # Django tự tạo Session và gửi Cookie về React
            return JsonResponse({"message": "Đăng nhập thành công"}, status=200)
        else:
            return JsonResponse({"error": "Sai tên đăng nhập hoặc mật khẩu"}, status=400)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Chỉ người đã đăng nhập mới gọi được
def get_user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        # Bạn có thể thêm các trường khác nếu muốn
    })