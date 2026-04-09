from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Kết nối 1-1 với bảng User mặc định của Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullname = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    # Các thông tin bổ sung cho App Anki
    streak = models.IntegerField(default=0)
    total_learned_cards = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
       if created:
        
        # 1. Tạo Profile mới
        Profile.objects.create(user=instance)
        
        # 2. CHỈ tự động vào group 'User' nếu họ KHÔNG phải là Staff/Superuser
        # (Người dùng đăng ký từ web bình thường sẽ không bao giờ có 2 quyền này)
        if not instance.is_staff and not instance.is_superuser:
            group, _ = Group.objects.get_or_create(name='User')
            instance.groups.add(group)
        
        
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
    # Đảm bảo profile luôn được lưu khi user thay đổi
       instance.profile.save()
