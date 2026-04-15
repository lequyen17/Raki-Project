from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Lấy dữ liệu mặc định (chỉ có access và refresh)
        data = super().validate(attrs)
        
        # Nhét thêm cục 'user' vào để React có cái mà hiển thị Header
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'is_staff': self.user.is_staff,
        }
        return data