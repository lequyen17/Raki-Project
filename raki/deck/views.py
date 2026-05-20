from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.services import DeckService


# =========================
# GET + CREATE DECK
# =========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_decks(request):
    if request.method == "POST":
        try:
            data = DeckService.create_deck(request.user, request.data)
            return Response(data, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
            
    #GET
    data = DeckService.get_user_decks(request.user)
    return Response(data)


# =========================
# MOVE DECK
# =========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_user_deck(request):
    try:
        data = DeckService.move_deck(request.user, request.data)
        return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)


# =========================
# DETAIL / UPDATE / DELETE
# =========================
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_deck_detail(request, deck_id):
    try:
        if request.method == "PUT":
            data = DeckService.update_deck(deck_id, request.user, request.data)
            return Response(data)
        elif request.method == "DELETE":
            data = DeckService.delete_deck(deck_id, request.user)
            return Response(data)
        else:
            data = DeckService.get_deck_detail(deck_id, request.user)
            return Response(data)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
