"""
URL configuration for raki project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
# Sử dụng 'as' để đặt tên riêng cho từng file views
from accounts import views as accounts_views
from deck import views as deck_views
from card import views as card_views
from note import views as note_views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from accounts.views import MyTokenLoginView
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Các route của accounts
    # Đường dẫn đăng nhập để lấy Token (thay cho login_view cũ)
    path('api/login/', MyTokenLoginView.as_view(), name='token_obtain_pair'),
    # Đường dẫn để lấy Access Token mới khi cái cũ hết hạn (Refresh Token)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/register/', accounts_views.register_view, name='register'),
    path('api/user/profile/', accounts_views.get_user_profile, name='user_profile'),
    path('api/user/profile/update/', accounts_views.update_user_profile, name='update_user_profile'),
    
    # Các route của deck
    path('api/user/decks/', deck_views.get_user_decks, name='user_decks'),
    path('api/user/decks/move/', deck_views.move_user_deck, name='move_user_deck'),
    path('api/user/decks/<int:deck_id>/', deck_views.user_deck_detail, name='user_deck_detail'),
    path('api/user/decks/<int:deck_id>/cards/', card_views.list_cards_by_deck, name='list_cards_by_deck'),
    
    # Các route của note
    path('api/user/note-types/', note_views.note_types_view, name='note_types'),
    path('api/user/decks/<int:deck_id>/notes/', note_views.create_note, name='create_note_by_deck'),
]