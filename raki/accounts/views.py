import json
from datetime import datetime, timedelta
from django.db.models import Count

django_jwt = True

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import Profile
import jwt

User = get_user_model()
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24  # 1 day


def _make_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def _get_user_profile_data(user):
    """
    Get user profile data. If profile doesn't exist, create one automatically.
    Returns tuple: (first_name, last_name, phone, streak)
    """
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        # Auto-create profile if it doesn't exist
        profile = Profile.objects.create(user=user)
    
    first_name = user.first_name or ''
    last_name = user.last_name or ''
    phone = profile.phone or ''
    streak = profile.streak
    
    return first_name, last_name, phone, streak


def _get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

    user_id = payload.get('user_id')
    if user_id is None:
        return None, 'Invalid token payload'

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None, 'User not found'

    return user, None


@csrf_exempt
@api_view(['POST'])
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        token = _make_token(user)
        first_name, last_name, phone, streak = _get_user_profile_data(user)
        
        # Count total cards owned by the user
        from flashcards.models import Card
        total_cards = Card.objects.filter(deck__user=user).count()
        total_learned_cards = user.profile.total_learned_cards
        
        return JsonResponse({
            'access': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'streak': streak,
                'total_cards': total_cards,
                'total_learned_cards': total_learned_cards,
                'is_staff': user.is_staff,
                'groups': list(user.groups.values_list('name', flat=True)),
            }
        }, status=200)

    return JsonResponse({'error': 'Sai tên đăng nhập hoặc mật khẩu'}, status=400)


@api_view(['GET'])
def get_user_profile(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response({'detail': 'Authorization header missing or invalid.'}, status=401)

    token = auth_header.split(' ', 1)[1]
    user, error = _get_user_from_token(token)
    if error:
        return Response({'detail': error}, status=401)

    first_name, last_name, phone, streak = _get_user_profile_data(user)
    
    # Count total cards owned by the user
    from flashcards.models import Card
    total_cards = Card.objects.filter(deck__user=user).count()
    
    # Get total learned cards from profile
    total_learned_cards = user.profile.total_learned_cards
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'streak': streak,
        'total_cards': total_cards,
        'total_learned_cards': total_learned_cards,
        'is_staff': user.is_staff,
        'groups': list(user.groups.values_list('name', flat=True)),
    })


@api_view(['PUT'])
def update_user_profile(request):
    """
    Update user profile: email, first_name, last_name, phone
    Requires authentication via Bearer token
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response({'detail': 'Authorization header missing or invalid.'}, status=401)

    token = auth_header.split(' ', 1)[1]
    user, error = _get_user_from_token(token)
    if error:
        return Response({'detail': error}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=400)

    # Get fields from request (all optional)
    email = data.get('email', user.email).strip()
    first_name = data.get('first_name', user.first_name).strip()
    last_name = data.get('last_name', user.last_name).strip()
    phone = data.get('phone', user.profile.phone or '').strip()

    # Validate email format if provided
    if email != user.email:
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Email không hợp lệ'}, status=400)

        # Check if email already exists
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response({'error': 'Email này đã được đăng ký'}, status=400)

    # Validate first_name and last_name length if provided
    if first_name and (len(first_name) < 2 or len(first_name) > 150):
        return Response({
            'error': 'Tên đầu phải từ 2 đến 150 ký tự'
        }, status=400)
    
    if last_name and (len(last_name) < 2 or len(last_name) > 150):
        return Response({
            'error': 'Họ phải từ 2 đến 150 ký tự'
        }, status=400)

    # Validate phone length if provided
    if phone and len(phone) > 15:
        return Response({
            'error': 'Số điện thoại không hợp lệ'
        }, status=400)

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
        from flashcards.models import Card
        total_cards = Card.objects.filter(deck__user=user).count()
        total_learned_cards = user.profile.total_learned_cards

        return Response({
            'success': True,
            'message': 'Cập nhật hồ sơ thành công!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.profile.phone,
                'streak': user.profile.streak,
                'total_cards': total_cards,
                'total_learned_cards': total_learned_cards,
            }
        }, status=200)

    except Exception as e:
        return Response({
            'error': f'Lỗi cập nhật hồ sơ: {str(e)}'
        }, status=500)


@api_view(['GET', 'POST'])
def get_user_decks(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response({'detail': 'Authorization header missing or invalid.'}, status=401)

    token = auth_header.split(' ', 1)[1]
    user, error = _get_user_from_token(token)
    if error:
        return Response({'detail': error}, status=401)

    from flashcards.models import Deck

    if request.method == 'POST':
        name = str(request.data.get('name', '')).strip()
        description = str(request.data.get('description', '')).strip()
        parent_id = request.data.get('parent_id')

        if not name:
            return Response({'error': 'Deck name is required.'}, status=400)

        if len(name) > 100:
            return Response({'error': 'Deck name must be at most 100 characters.'}, status=400)

        parent = None
        if parent_id not in (None, '', 'null'):
            try:
                parent = Deck.objects.get(id=parent_id, user=user)
            except Deck.DoesNotExist:
                return Response({'error': 'Parent deck not found.'}, status=404)

        deck = Deck.objects.create(
            user=user,
            name=name,
            description=description,
            parent=parent,
        )

        return Response({
            'id': deck.id,
            'name': deck.name,
            'description': deck.description or '',
            'total_cards': 0,
            'parent_id': deck.parent_id,
            'created_at': deck.created_at,
        }, status=201)

    decks = (
        Deck.objects
        .filter(user=user)
        .annotate(total_cards=Count('cards'))
        .order_by('name')
    )

    return Response({
        'count': decks.count(),
        'results': [
            {
                'id': deck.id,
                'name': deck.name,
                'description': deck.description or '',
                'total_cards': deck.total_cards,
                'parent_id': deck.parent_id,
                'created_at': deck.created_at,
            }
            for deck in decks
        ]
    })


@api_view(['POST'])
def move_user_deck(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response({'detail': 'Authorization header missing or invalid.'}, status=401)

    token = auth_header.split(' ', 1)[1]
    user, error = _get_user_from_token(token)
    if error:
        return Response({'detail': error}, status=401)

    from flashcards.models import Deck

    deck_id = request.data.get('deck_id')
    parent_id = request.data.get('parent_id')

    if not deck_id:
        return Response({'error': 'deck_id is required.'}, status=400)

    try:
        deck = Deck.objects.get(id=deck_id, user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found.'}, status=404)

    if parent_id in (None, '', 'null'):
        return Response({'error': 'Dropping to empty space is not allowed.'}, status=400)

    try:
        parent = Deck.objects.get(id=parent_id, user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Target parent deck not found.'}, status=404)

    if parent.id == deck.id:
        return Response({'error': 'A deck cannot be moved into itself.'}, status=400)

    cursor = parent
    while cursor is not None:
        if cursor.id == deck.id:
            return Response({'error': 'Cannot move a deck into its own subdeck.'}, status=400)
        cursor = cursor.parent

    deck.parent = parent
    deck.save(update_fields=['parent'])

    return Response({
        'success': True,
        'deck_id': deck.id,
        'parent_id': deck.parent_id,
    })


@csrf_exempt
@api_view(['POST'])
def register_view(request):
    """
    Register a new user with username, password, email, first_name, last_name, phone
    Validates input and saves to User and Profile tables
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    email = data.get('email', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone = data.get('phone', '').strip()

    # Validate all required fields
    if not all([username, password, confirm_password, email, first_name, last_name]):
        return JsonResponse({
            'error': 'Vui lòng điền đầy đủ tất cả các trường bắt buộc'
        }, status=400)

    # Validate username length and format
    if len(username) < 3:
        return JsonResponse({
            'error': 'Tên đăng nhập phải có ít nhất 3 ký tự'
        }, status=400)

    if len(username) > 150:
        return JsonResponse({
            'error': 'Tên đăng nhập không được vượt quá 150 ký tự'
        }, status=400)

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'error': 'Tên đăng nhập đã tồn tại'
        }, status=400)

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({
            'error': 'Email không hợp lệ'
        }, status=400)

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'error': 'Email này đã được đăng ký'
        }, status=400)

    # Validate password
    if len(password) < 6:
        return JsonResponse({
            'error': 'Mật khẩu phải có ít nhất 6 ký tự'
        }, status=400)

    # Check password confirmation
    if password != confirm_password:
        return JsonResponse({
            'error': 'Mật khẩu xác nhận không khớp'
        }, status=400)

    # Validate first_name and last_name length
    if len(first_name) < 2 or len(first_name) > 150:
        return JsonResponse({
            'error': 'Tên đầu phải từ 2 đến 150 ký tự'
        }, status=400)
    
    if len(last_name) < 2 or len(last_name) > 150:
        return JsonResponse({
            'error': 'Họ phải từ 2 đến 150 ký tự'
        }, status=400)

    # Validate phone (if provided)
    if phone and len(phone) > 15:
        return JsonResponse({
            'error': 'Số điện thoại không hợp lệ'
        }, status=400)

    try:
        # Create user with first_name and last_name
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Update profile with phone
        profile = user.profile
        profile.phone = phone
        profile.save()

        # Return success with user data
        return JsonResponse({
            'success': True,
            'message': 'Đăng ký thành công!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': profile.phone,
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'error': f'Lỗi đăng ký: {str(e)}'
        }, status=500)