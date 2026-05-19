from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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

        name = validated_data["name"]
        description = validated_data["description"]

        deck = DeckRepository.create_user_deck(
            user=user,
            name=name,
            description=description,
        )

        return Response(
            {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description or "",
                "total_cards": 0,
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

    DeckRepository.move_deck(
        deck,
        parent,
    )

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
        name = validated_data["name"]
        description = validated_data["description"]

        deck = DeckRepository.update_deck(
            deck=deck,
            name=name,
            description=description,
        )

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

        DeckRepository.delete_deck(deck)

        return Response({"success": True})

    # GET DETAIL
    has_subdecks = DeckRepository.has_subdecks(
        deck,
        user,
    )

    # Lấy cả deck hiện tại và tất cả deck con cháu
    def get_descendants(d):

        descendants = [d.id]

        children = DeckRepository.get_child_decks(
            d,
            user,
        )

        for child in children:
            descendants.extend(get_descendants(child))

        return descendants

    all_deck_ids = get_descendants(deck)

    cards_qs = DeckRepository.get_cards_by_deck_ids(all_deck_ids)

    progress_qs = CardRepository.get_progress_by_cards_and_user(
        cards_qs,
        user,
    )

    total_cards = cards_qs.count()

    progress_count = progress_qs.count()

    now = timezone.now()

    new_count = (total_cards - progress_count) + progress_qs.filter(
        repetition=0
    ).count()

    learn_count = progress_qs.filter(
        repetition__gt=0,
        interval__lt=7,
    ).count()

    review_count = progress_qs.filter(
        interval__gte=7,
        next_review__lte=now,
    ).count()

    return Response(
        {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "is_leaf": not has_subdecks,
            "stats": {
                "new": new_count,
                "learn": learn_count,
                "review": review_count,
                "total": total_cards,
            },
        }
    )
