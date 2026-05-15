from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Lấy dữ liệu mặc định (chỉ có access và refresh)
        data = super().validate(attrs)

        # Nhét thêm 'user'
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "name": f"{self.user.first_name} {self.user.last_name}".strip(),
            "is_staff": self.user.is_staff,
        }
        return data
