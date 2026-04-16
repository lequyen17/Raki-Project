from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.models import Deck
from card.models import Card


# =========================
# GET + CREATE DECK
# =========================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_user_decks(request):
    user = request.user

    if request.method == 'POST':
        name = str(request.data.get('name', '')).strip()
        description = str(request.data.get('description', '')).strip()

        if not name:
            return Response({'error': 'Deck name is required.'}, status=400)

        if len(name) > 100:
            return Response({'error': 'Deck name must be at most 100 characters.'}, status=400)

        deck = Deck.objects.create(
            user=user,
            name=name,
            description=description,
            parent=None,
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
        .annotate(total_cards=Count('notes__cards'))
        .order_by('name')
    )

    results = []
    for deck in decks:
        item = {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description or '',
            'total_cards': deck.total_cards,
            'parent_id': deck.parent_id,
            'created_at': deck.created_at,
        }
        results.append(item)

    # Trả về kết quả
    return Response({
        'count': decks.count(),
        'results': results
    })


# =========================
# MOVE DECK
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_user_deck(request):
    user = request.user

    deck_id = request.data.get('deck_id')
    parent_id = request.data.get('parent_id')

    if not deck_id:
        return Response({'error': 'deck_id is required.'}, status=400)

    try:
        deck = Deck.objects.get(id=deck_id, user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found.'}, status=404)

    parent = None
    if parent_id not in (None, '', 'null'):
        try:
            parent = Deck.objects.get(id=parent_id, user=user)
        except Deck.DoesNotExist:
            return Response({'error': 'Target parent deck not found.'}, status=404)

        if parent.id == deck.id:
            return Response({'error': 'A deck cannot be moved into itself.'}, status=400)

        # tránh loop
        cursor = parent
        while cursor:
            if cursor.id == deck.id:
                return Response({'error': 'Cannot move into its own subdeck.'}, status=400)
            cursor = cursor.parent

    deck.parent = parent
    deck.save(update_fields=['parent'])

    return Response({
        'success': True,
        'deck_id': deck.id,
        'parent_id': deck.parent_id,
    })


# =========================
# DETAIL / UPDATE / DELETE
# =========================
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_deck_detail(request, deck_id):
    user = request.user

    try:
        deck = Deck.objects.get(id=deck_id, user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found.'}, status=404)

    # UPDATE
    if request.method == 'PUT':
        name = str(request.data.get('name', deck.name)).strip()
        description = str(request.data.get('description', deck.description or '')).strip()

        if not name:
            return Response({'error': 'Deck name is required.'}, status=400)

        if len(name) > 100:
            return Response({'error': 'Deck name must be at most 100 characters.'}, status=400)

        deck.name = name
        deck.description = description
        deck.save(update_fields=['name', 'description'])

        return Response({
            'id': deck.id,
            'name': deck.name,
            'description': deck.description or '',
            'parent_id': deck.parent_id,
        })

    # DELETE
    if request.method == 'DELETE':
        deck.delete()
        return Response({'success': True})

    # GET DETAIL
    has_subdecks = Deck.objects.filter(parent=deck, user=user).exists()
    cards_qs = Card.objects.filter(note_id__deck_id=deck)
    now = timezone.now()

    new_count = cards_qs.filter(repetition=0).count()
    learn_count = cards_qs.filter(repetition__gt=0, interval__lt=7).count()
    review_count = cards_qs.filter(interval__gte=7, next_review__lte=now).count()

    return Response({
        'id': deck.id,
        'name': deck.name,
        'description': deck.description or '',
        'is_leaf': not has_subdecks,
        'stats': {
            'new': new_count,
            'learn': learn_count,
            'review': review_count,
            'total': cards_qs.count(),
        }
    })