from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Kết nối 1-1 với bảng User mặc định của Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    # Các thông tin bổ sung cho App Anki
    streak = models.IntegerField(default=0)
    total_learned_cards = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when a new User is created"""
    if created:
        # Tạo Profile mới
        Profile.objects.create(user=instance)
        
        # CHỈ tự động vào group 'User' nếu họ KHÔNG phải là Staff/Superuser
        if not instance.is_staff and not instance.is_superuser:
            group, _ = Group.objects.get_or_create(name='User')
            instance.groups.add(group)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile exists and save it when user changes"""
    # Nếu profile không tồn tại, tạo nó
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
