from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.repositories import DeckRepository
from .repositories import CardRepository
from card.services.review_service import ReviewService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):

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

    cards = CardRepository.get_cards_by_deck_ids_ordered(all_deck_ids)

    progress_dict = CardRepository.get_progress_dict(
        cards,
        user,
    )

    results = []

    for card in cards:

        p = progress_dict.get(card.id)

        results.append(
            {
                "id": card.id,
                "repetition": p.repetition if p else 0,
                "interval": p.interval if p else 1,
                "easiness": p.easiness if p else 2.5,
                "next_review": p.next_review if p else None,
                "cloze_index": card.cloze_index,
            }
        )

    return Response(
        {
            "deck_id": deck.id,
            "deck_name": deck.name,
            "count": cards.count(),
            "results": results,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_study_cards(request, deck_id):

    user = request.user

    today = timezone.localdate()

    deck = DeckRepository.get_deck_for_user(
        deck_id,
        user,
    )

    if not deck:
        return Response(
            {"error": "Deck not found."},
            status=404,
        )

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

    # 1. Đếm số thẻ mới đã học hôm nay
    new_already_started_today = CardRepository.count_started_new_today(
        all_deck_ids,
        user,
        today,
    )

    NEW_LIMIT_PER_DAY = 20

    remaining_new_quota = max(
        0,
        NEW_LIMIT_PER_DAY - new_already_started_today,
    )

    # 2. Lấy cards + progress
    cards = CardRepository.get_cards_by_deck_ids(all_deck_ids)

    progress_dict = CardRepository.get_progress_dict(
        cards,
        user,
    )

    # 3. Build study session
    results = []

    session_new_count = 0
    session_learning_count = 0
    session_review_count = 0

    for card in cards:

        p = progress_dict.get(card.id)

        if not p:

            if session_new_count < remaining_new_quota:
                status = "new"
                session_new_count += 1
            else:
                continue

        elif p.next_review <= today:

            status = p.status

            if status == "learning":
                session_learning_count += 1

            elif status == "review":
                session_review_count += 1

        else:
            continue

        field_values = {fv.definition.name: fv.value for fv in card.note.values.all()}

        results.append(
            {
                "id": card.id,
                "status": status,
                "cloze_index": card.cloze_index,
                "template": {
                    "front": card.template.front,
                    "back": card.template.back,
                },
                "field_values": field_values,
            }
        )

    # 4. Overall stats
    overall_new = 0
    overall_learning = 0
    overall_review = 0

    easiness_sum = 0
    easiness_count = 0

    for card in cards:

        p = progress_dict.get(card.id)

        if not p:

            overall_new += 1

        else:

            if p.status == "learning":
                overall_learning += 1

            elif p.status == "review":

                overall_review += 1

                easiness_sum += p.easiness
                easiness_count += 1

    avg_ease = easiness_sum / easiness_count if easiness_count > 0 else 2.5

    return Response(
        {
            "deck_id": deck.id,
            "name": deck.name,
            "description": deck.description,
            "counts": {
                "new": session_new_count,
                "learning": session_learning_count,
                "review": session_review_count,
                "total": len(results),
                "today_completed_new": (new_already_started_today),
            },
            "overall_stats": {
                "total": len(cards),
                "new": overall_new,
                "learning": overall_learning,
                "review": overall_review,
                "average_ease": avg_ease,
            },
            "results": results,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_card(request, card_id):

    user = request.user

    card = CardRepository.get_card_for_review(
        card_id,
        user,
    )

    if not card:
        return Response(
            {"error": "Card not found."},
            status=404,
        )

    quality = request.data.get("quality")

    if quality not in [
        "again",
        "hard",
        "good",
        "easy",
    ]:
        return Response(
            {"error": "Invalid quality."},
            status=400,
        )

    p, created = CardRepository.get_or_create_progress(
        user,
        card,
    )

    service = ReviewService()

    updated_progress = service.review_card(
        p,
        quality,
    )

    return Response(
        {
            "success": True,
            "interval": updated_progress.interval,
            "status": updated_progress.status,
        }
    )
