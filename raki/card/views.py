from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.repositories import DeckRepository
from card.repositories import CardRepository
from card.services.main_service import CardMainService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):
    user = request.user
    deck = DeckRepository.get_deck_for_user(deck_id, user)

    if not deck:
        return Response({"error": "Deck not found."}, status=404)

    data = CardMainService.list_cards_by_deck(deck, user)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_study_cards(request, deck_id):
    user = request.user
    deck = DeckRepository.get_deck_for_user(deck_id, user)

    if not deck:
        return Response({"error": "Deck not found."}, status=404)

    data = CardMainService.get_study_cards(deck, user)
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_card(request, card_id):
    user = request.user
    card = CardRepository.get_card_for_review(card_id, user)

    if not card:
        return Response({"error": "Card not found."}, status=404)

    try:
        data = CardMainService.review_card(card, user, request.data)
        return Response(data)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
