from rest_framework.decorators import api_view
from rest_framework.response import Response

# from accounts.views import _get_user_from_token
# from card.models import Card
# from deck.models import Deck


# @api_view(['GET'])
# def list_cards_by_deck(request, deck_id):
#     auth_header = request.META.get('HTTP_AUTHORIZATION', '')
#     if not auth_header.startswith('Bearer '):
#         return Response({'detail': 'Authorization header missing or invalid.'}, status=401)

#     token = auth_header.split(' ', 1)[1]
#     user, error = _get_user_from_token(token)
#     if error:
#         return Response({'detail': error}, status=401)

#     try:
#         deck = Deck.objects.get(id=deck_id, user=user)
#     except Deck.DoesNotExist:
#         return Response({'error': 'Deck not found.'}, status=404)

#     cards = (
#         Card.objects
#         .filter(note_id__deck_id=deck)
#         .order_by('-created_at')
#     )

#     return Response({
#         'deck_id': deck.id,
#         'deck_name': deck.name,
#         'count': cards.count(),
#         'results': [
#             {
#                 'id': card.id,
#                 'repetition': card.repetition,
#                 'interval': card.interval,
#                 'easiness': card.easiness,
#                 'next_review': card.next_review,
#                 'created_at': card.created_at,
#             }
#             for card in cards
#         ],
#     })
