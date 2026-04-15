from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.models import Deck
from card.models import Card


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):
    user = request.user

    try:
        deck = Deck.objects.get(id=deck_id, user=user)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found.'}, status=404)

    cards = (
        Card.objects
        .filter(note_id__deck_id=deck)
        .order_by('-created_at')
    )

    return Response({
        'deck_id': deck.id,
        'deck_name': deck.name,
        'count': cards.count(),
        'results': [
            {
                'id': card.id,
                'repetition': card.repetition,
                'interval': card.interval,
                'easiness': card.easiness,
                'next_review': card.next_review,
                'created_at': card.created_at,
            }
            for card in cards
        ],
    })