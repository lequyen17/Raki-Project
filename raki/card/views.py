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