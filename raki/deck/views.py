from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.services import DeckService

from .repositories import DeckRepository
from card.repositories import CardRepository
from .serializers import DeckValidator, DeckMoveValidator


# =========================
# GET + CREATE DECK
# =========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_decks(request):

    user = request.user

    # CREATE
    if request.method == "POST":
        try:
            validated_data = DeckValidator.validate(request.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        deck = DeckService.create_deck(user, validated_data)

        return Response(
            {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description or "",
                "parent_id": deck.parent_id,
                "created_at": deck.created_at,
            },
            status=201,
        )

    # GET
    decks = DeckRepository.get_user_decks(user)

    results = []

    for deck in decks:
        results.append(
            {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description or "",
                "total_cards": deck.total_cards,
                "parent_id": deck.parent_id,
                "created_at": deck.created_at,
            }
        )

    return Response(
        {
            "count": decks.count(),
            "results": results,
        }
    )


# =========================
# MOVE DECK
# =========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_user_deck(request):

    user = request.user

    try:
        validated_data = DeckMoveValidator.validate(request.data, user)
    except LookupError as e:

        return Response({"error": str(e)}, status=404)
    except ValueError as e:

        return Response({"error": str(e)}, status=400)

    deck = validated_data["deck"]
    parent = validated_data["parent"]

    DeckService.move_deck(deck, parent)

    return Response(
        {
            "success": True,
            "deck_id": deck.id,
            "parent_id": deck.parent_id,
        }
    )


# =========================
# DETAIL / UPDATE / DELETE
# =========================
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_deck_detail(request, deck_id):

    user = request.user

    deck = DeckRepository.get_deck_for_user(
        deck_id,
        user,
    )

    if not deck:
        return Response(
            {"error": "Deck not found."},
            status=404,
        )

    # UPDATE
    if request.method == "PUT":

        try:
            validated_data = DeckValidator.validate(request.data, deck)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        deck = DeckService.update_deck(deck, validated_data)

        return Response(
            {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description or "",
                "parent_id": deck.parent_id,
            }
        )

    # DELETE
    if request.method == "DELETE":

        DeckService.delete_deck(deck)

        return Response({"success": True})

    # GET DETAIL
    has_subdecks = DeckRepository.has_subdecks(
        deck,
        user,
    )

    stats = DeckService.get_deck_stats(deck, user)

    return Response(
        {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "is_leaf": not has_subdecks,
            "stats": stats,
        }
    )
