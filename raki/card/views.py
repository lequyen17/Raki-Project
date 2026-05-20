from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from card.services.main_service import CardMainService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):
    try:
        data = CardMainService.list_cards_by_deck(deck_id, request.user)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_study_cards(request, deck_id):
    try:
        data = CardMainService.get_study_cards(deck_id, request.user)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_card(request, card_id):
    try:
        data = CardMainService.review_card(card_id, request.user, request.data)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
