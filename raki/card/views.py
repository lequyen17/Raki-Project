from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.models import Deck
from card.models import Card
from progress.models import Progress


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):
    user = request.user

    try:
        deck = Deck.objects.get(id=deck_id, deck_users__user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found.'}, status=404)

    def get_descendants(d):
        descendants = [d.id]
        children = Deck.objects.filter(parent=d, deck_users__user=user)
        for child in children:
            descendants.extend(get_descendants(child))
        return descendants
        
    all_deck_ids = get_descendants(deck)

    cards = (
        Card.objects
        .filter(note__deck_id__in=all_deck_ids)
        .order_by('-id')
    )
    
    progress_dict = {
        p.card_id: p for p in Progress.objects.filter(card__in=cards, user=user)
    }

    results = []
    for card in cards:
        p = progress_dict.get(card.id)
        results.append({
            'id': card.id,
            'repetition': p.repetition if p else 0,
            'interval': p.interval if p else 0,
            'easiness': p.easiness if p else 2.5,
            'next_review': p.next_review if p else None,
        })

    return Response({
        'deck_id': deck.id,
        'deck_name': deck.name,
        'count': cards.count(),
        'results': results,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_cards(request, deck_id):
    user = request.user
    try:
        deck = Deck.objects.get(id=deck_id, deck_users__user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found.'}, status=404)

    def get_descendants(d):
        descendants = [d.id]
        children = Deck.objects.filter(parent=d, deck_users__user=user)
        for child in children:
            descendants.extend(get_descendants(child))
        return descendants
        
    all_deck_ids = get_descendants(deck)

    cards = Card.objects.filter(note__deck_id__in=all_deck_ids).select_related('note', 'template').prefetch_related('note__values__definition')
    
    now = timezone.now()
    progress_dict = {
        p.card_id: p for p in Progress.objects.filter(card__in=cards, user=user)
    }

    results = []
    new_count = 0
    learning_count = 0
    review_count = 0

    for card in cards:
        p = progress_dict.get(card.id)
        
        status = None
        if not p:
            status = 'New'
            new_count += 1
        elif p.next_review <= now:
            if p.interval < 7:
                status = 'Learning'
                learning_count += 1
            else:
                status = 'Review'
                review_count += 1
        
        if status:
            field_values = {fv.definition.name: fv.value for fv in card.note.values.all()}
            results.append({
                'id': card.id,
                'status': status,
                'template': {
                    'front': card.template.front,
                    'back': card.template.back,
                },
                'field_values': field_values
            })

    return Response({
        'deck_id': deck.id,
        'deck_name': deck.name,
        'counts': {
            'new': new_count,
            'learning': learning_count,
            'review': review_count,
            'total': len(results)
        },
        'results': results
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_card(request, card_id):
    user = request.user
    try:
        # Kiểm tra Card tồn tại và thuộc sở hữu của user
        card = Card.objects.get(id=card_id, note__deck__deck_users__user=user)
    except Card.DoesNotExist:
        return Response({'error': 'Card not found.'}, status=404)
        
    quality = request.data.get('quality')
    if quality not in ['again', 'hard', 'good', 'easy']:
        return Response({'error': 'Invalid quality.'}, status=400)

    p, created = Progress.objects.get_or_create(user=user, card=card, defaults={
        'repetition': 0, 'interval': 0, 'easiness': 2.5, 'next_review': timezone.now()
    })

    # SM-2 logic
    if quality == 'again':
        p.repetition = 0
        p.interval = 0
        p.easiness = max(1.3, p.easiness - 0.8)
    elif quality == 'hard':
        if p.repetition == 0:
            p.interval = 1
        else:
            p.interval = max(1, int(p.interval * 1.2))
        p.repetition += 1
        p.easiness = max(1.3, p.easiness - 0.15)
    elif quality == 'good':
        if p.repetition == 0:
            p.interval = 1
        elif p.repetition == 1:
            p.interval = 6
        else:
            p.interval = max(1, int(p.interval * p.easiness))
        p.repetition += 1
    elif quality == 'easy':
        p.easiness += 0.15
        if p.repetition == 0:
            p.interval = 4
        else:
            p.interval = max(1, int(p.interval * p.easiness * 1.3))
        p.repetition += 1
        
    now = timezone.now()
    if quality == 'again':
        p.next_review = now + timedelta(minutes=1)
    else:
        p.next_review = now + timedelta(days=p.interval)
        
    p.save()
    
    return Response({'success': True})