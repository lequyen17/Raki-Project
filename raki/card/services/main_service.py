from django.utils import timezone

from deck.repositories import DeckRepository
from card.repositories import CardRepository
from card.services.review_service import ReviewService


class CardMainService:
    @staticmethod
    def _serialize_card_content(card):
        return {
            "template": {
                "front": card.template.front,
                "back": card.template.back,
            },
            "field_values": [
                {"name": fv.definition.name, "value": fv.value}
                for fv in card.note.values.all()
            ],
        }

    @staticmethod
    def list_cards_by_deck(deck_id, user):
        deck = DeckRepository.get_deck_for_user(deck_id, user)
        if not deck:
            raise LookupError("DECK_NOT_FOUND")

        def get_descendants(d):
            descendants = [d.id]
            children = DeckRepository.get_child_decks(d, user)
            for child in children:
                descendants.extend(get_descendants(child))
            return descendants

        all_deck_ids = get_descendants(deck)
        cards = CardRepository.get_cards_by_deck_ids_ordered(all_deck_ids)
        progress_dict = CardRepository.get_progress_dict(cards, user)

        from deck.models import UserDeck

        owner_deck_ids = set(
            UserDeck.objects.filter(user=user, role="owner").values_list(
                "deck_id", flat=True
            )
        )

        results = []
        for card in cards:
            p = progress_dict.get(card.id)
            content = CardMainService._serialize_card_content(card)
            results.append(
                {
                    "id": card.id,
                    "repetition": p.repetition if p else 0,
                    "interval": p.interval if p else 1,
                    "easiness": p.easiness if p else 2.5,
                    "next_review": p.next_review if p else None,
                    "cloze_index": card.cloze_index,
                    "is_owner": card.note.deck_id in owner_deck_ids,
                    **content,
                }
            )

        return {
            "deck_id": deck.id,
            "deck_name": deck.name,
            "count": cards.count(),
            "results": results,
        }

    @staticmethod
    def get_card_detail(card_id, user):
        card = CardRepository.get_card_by_id(card_id, user)
        if not card:
            raise LookupError("CARD_NOT_FOUND")

        from deck.models import UserDeck

        is_owner = UserDeck.objects.filter(
            user=user, deck=card.note.deck, role="owner"
        ).exists()

        content = CardMainService._serialize_card_content(card)
        return {
            "id": card.id,
            "cloze_index": card.cloze_index,
            **content,
            "is_owner": is_owner,
        }

    @staticmethod
    def get_study_cards(deck_id, user):
        deck = DeckRepository.get_deck_for_user(deck_id, user)
        if not deck:
            raise LookupError("DECK_NOT_FOUND")

        today = timezone.localdate()

        def get_descendants(d):
            descendants = [d.id]
            children = DeckRepository.get_child_decks(d, user)
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
        remaining_new_quota = max(0, NEW_LIMIT_PER_DAY - new_already_started_today)

        # 2. Lấy cards + progress
        cards = CardRepository.get_cards_by_deck_ids(all_deck_ids)
        progress_dict = CardRepository.get_progress_dict(cards, user)

        # 3. Build study session
        results = []

        for card in cards:
            p = progress_dict.get(card.id)

            if not p:
                if (
                    len([r for r in results if r["status"] == "new"])
                    < remaining_new_quota
                ):
                    status = "new"
                else:
                    continue
            elif p.next_review <= today:
                status = p.status
            else:
                continue

            content = CardMainService._serialize_card_content(card)
            results.append(
                {
                    "id": card.id,
                    "status": status,
                    "cloze_index": card.cloze_index,
                    **content,
                }
            )

        return {
            "deck_name": deck.name,
            "results": results,
        }

    @staticmethod
    def review_card(card_id, user, validated_data):
        card = CardRepository.get_card_for_review(card_id, user)
        if not card:
            raise LookupError("CARD_NOT_FOUND")

        quality = validated_data["quality"]

        p, created = CardRepository.get_or_create_progress(user, card)
        service = ReviewService()
        updated_progress = service.review_card(p, quality)

        return {
            "success": True,
            "interval": updated_progress.interval,
            "status": updated_progress.status,
        }

    @staticmethod
    def update_card(card_id, user, field_values_list):
        card = CardRepository.get_card_for_owner(card_id, user)
        if not card:
            raise LookupError("CARD_NOT_FOUND_OR_NOT_OWNER")

        data_dict = {item["name"]: item["value"] for item in field_values_list}

        # 3. Cập nhật vào Database
        for fv in card.note.values.all():
            field_name = fv.definition.name
            if field_name in data_dict:
                fv.value = data_dict[field_name]
                fv.save()

        # 4. Cấu trúc lại dữ liệu trả về theo đúng định dạng List của Serializer
        # Để khớp với CardDetailResponseSerializer (field_values = CardDetailValueSerializer(many=True))
        updated_fields_response = [
            {"name": fv.definition.name, "value": fv.value}
            for fv in card.note.values.all()
        ]
        return {
            "id": card.id,
            "cloze_index": card.cloze_index,
            "template": {
                "front": card.template.front,
                "back": card.template.back,
            },
            "field_values": updated_fields_response,
        }

    @staticmethod
    def delete_card(card_id, user):
        success = CardRepository.delete_card(card_id, user)
        if not success:
            raise LookupError("CARD_NOT_FOUND")
        return {"success": True}
