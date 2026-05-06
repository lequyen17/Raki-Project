from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.models import Deck
from card.models import Card
from progress.models import Progress


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cards_by_deck(request, deck_id):
    user = request.user

    try:
        deck = Deck.objects.get(id=deck_id, deck_users__user=user)
    except Deck.DoesNotExist:
        return Response({"error": "Deck not found."}, status=404)

    def get_descendants(d):
        descendants = [d.id]
        children = Deck.objects.filter(parent=d, deck_users__user=user)
        for child in children:
            descendants.extend(get_descendants(child))
        return descendants

    all_deck_ids = get_descendants(deck)

    cards = Card.objects.filter(note__deck_id__in=all_deck_ids).order_by("-id")

    progress_dict = {
        p.card_id: p for p in Progress.objects.filter(card__in=cards, user=user)
    }

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

    try:
        deck = Deck.objects.get(id=deck_id, deck_users__user=user)
    except Deck.DoesNotExist:
        return Response({"error": "Deck not found."}, status=404)

    def get_descendants(d):
        descendants = [d.id]
        children = Deck.objects.filter(parent=d, deck_users__user=user)
        for child in children:
            descendants.extend(get_descendants(child))
        return descendants

    all_deck_ids = get_descendants(deck)

    # 1. Đếm số thẻ MỚI đã bắt đầu học trong hôm nay (dựa trên created_at)
    new_already_started_today = Progress.objects.filter(
        card__note__deck_id__in=all_deck_ids, user=user, created_at__date=today
    ).count()

    # Giới hạn còn lại cho thẻ mới (Quota)
    NEW_LIMIT_PER_DAY = 20
    remaining_new_quota = max(0, NEW_LIMIT_PER_DAY - new_already_started_today)

    # 2. Lấy toàn bộ cards và progress hiện có
    cards = (
        Card.objects.filter(note__deck_id__in=all_deck_ids)
        .select_related("note", "template")
        .prefetch_related("note__values__definition")
    )

    progress_dict = {
        p.card_id: p for p in Progress.objects.filter(card__in=cards, user=user)
    }

    # 3. Duyệt danh sách để lọc thẻ cho Session này
    results = []
    session_new_count = 0
    session_learning_count = 0
    session_review_count = 0

    for card in cards:
        p = progress_dict.get(card.id)

        if not p:
            # Chỉ lấy thẻ NEW nếu chưa vượt quá giới hạn ngày hôm nay
            if session_new_count < remaining_new_quota:
                status = "new"
                session_new_count += 1
            else:
                continue
        elif p.next_review <= today:
            # Thẻ cũ đến hạn (không bị giới hạn bởi NEW_LIMIT)
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

    # 4. Tính toán overall stats cho view
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

    avg_ease = (easiness_sum / easiness_count) if easiness_count > 0 else 2.5

    # 5. Trả về kết quả kèm các con số thống kê
    return Response(
        {
            "deck_id": deck.id,
            "name": deck.name,
            "description": deck.description,
            "counts": {
                "new": session_new_count,  # Số thẻ mới nạp thêm hôm nay
                "learning": session_learning_count,  # Số thẻ đang học dở
                "review": session_review_count,  # Số thẻ ôn tập đến hạn
                "total": len(results),
                "today_completed_new": new_already_started_today,  # Số thẻ mới đã nạp thành công trong ngày
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
    try:
        # Kiểm tra Card tồn tại và thuộc sở hữu của user
        card = Card.objects.get(id=card_id, note__deck__deck_users__user=user)
    except Card.DoesNotExist:
        return Response({"error": "Card not found."}, status=404)

    quality = request.data.get("quality")
    if quality not in ["again", "hard", "good", "easy"]:
        return Response({"error": "Invalid quality."}, status=400)

    p, created = Progress.objects.get_or_create(
        user=user,
        card=card,
        defaults={
            "status": "learning",
            "repetition": 0,
            "interval": 1,
            "easiness": 2.5,
            "next_review": timezone.localdate(),
        },
    )

    today = timezone.localdate()

    # =========================
    # 1. LEARNING PHASE
    # =========================
    if p.status == "learning":
        p.interval = 0

        if quality == "again":
            p.repetition = 0
            p.status = "learning"

        elif quality == "hard":
            p.repetition = 0  # cho vào cuối learning queue

        elif quality == "good":
            p.repetition += 1
            if p.repetition >= 2:
                p.status = "review"
                p.repetition = 0
                p.interval = 1

        elif quality == "easy":
            p.status = "review"
            p.repetition = 0
            p.interval = 1

    # =========================
    # 2. REVIEW PHASE (SM-2)
    # =========================
    else:
        E = p.easiness

        if quality == "again":
            q = 0
            p.repetition = 0
            p.interval = 0
            p.status = "learning"

        elif quality == "hard":
            q = 3
            p.repetition = 0
            p.interval = max(1, int(p.interval * 1.2))

        elif quality == "good":
            q = 4
            if p.repetition == 0:
                p.interval = 1
            elif p.repetition == 1:
                p.interval = 6
            else:
                p.interval = max(1, int(p.interval * E))
            p.repetition += 1

        elif quality == "easy":
            q = 5
            if p.repetition == 0:
                p.interval = 4
            else:
                p.interval = max(1, int(p.interval * E * 1.3))
            p.repetition += 1

        # =========================
        # update easiness SM-2 formula
        # =========================
        p.easiness = max(1.3, E + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))

    p.next_review = today + timedelta(days=p.interval)

    p.save()

    return Response({"success": True, "interval": p.interval, "status": p.status})
