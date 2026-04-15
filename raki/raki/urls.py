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

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Các route của accounts
    path('api/login/', accounts_views.login_view, name='login'),
    path('api/register/', accounts_views.register_view, name='register'),
    path('api/user/profile/', accounts_views.get_user_profile, name='user_profile'),
    path('api/user/profile/update/', accounts_views.update_user_profile, name='update_user_profile'),
    
    # Các route của deck
    path('api/user/decks/', deck_views.get_user_decks, name='user_decks'),
    path('api/user/decks/move/', deck_views.move_user_deck, name='move_user_deck'),
    path('api/user/decks/<int:deck_id>/', deck_views.user_deck_detail, name='user_deck_detail'),
]