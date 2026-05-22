from django.utils import timezone

from deck.repositories import DeckRepository
from card.repositories import CardRepository


class DeckService:

    @staticmethod
    def _get_deck_or_404(deck_id, user):
        deck = DeckRepository.get_deck_for_user(deck_id, user)
        if not deck:
            raise LookupError("Deck not found.")
        return deck

    # =========================
    # CREATE
    # =========================
    @staticmethod
    def create_deck(user, validated_data):
        deck = DeckRepository.create_user_deck(
            user=user,
            name=validated_data["name"],
            description=validated_data["description"],
        )
        return {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "parent_id": deck.parent_id,
            "created_at": deck.created_at,
        }

    # =========================
    # GET ALL USER DECKS
    # =========================
    @staticmethod
    def get_user_decks(user):
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
        return {
            "count": decks.count(),
            "results": results,
        }

    # =========================
    # UPDATE
    # =========================
    @staticmethod
    def update_deck(deck, validated_data):
        deck = DeckRepository.update_deck(
            deck=deck,
            name=validated_data["name"],
            description=validated_data["description"],
        )
        return {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "parent_id": deck.parent_id,
            "created_at": deck.created_at,
        }

    # =========================
    # MOVE (business rule nằm ở service)
    # =========================
    @staticmethod
    def move_deck(validated_data):
        deck = validated_data["deck"]
        parent = validated_data["parent"]
        DeckRepository.move_deck(deck, parent)
        return {
            "success": True,
            "deck_id": deck.id,
            "parent_id": deck.parent_id,
        }

    # =========================
    # DELETE
    # =========================
    @staticmethod
    def delete_deck(deck_id, user):
        deck = DeckService._get_deck_or_404(deck_id, user)
        DeckRepository.delete_deck(deck)
        return {"success": True}

    # =========================
    # DESCENDANTS TREE
    # =========================
    @staticmethod
    def get_descendant_ids(deck, user):

        def dfs(node):
            ids = [node.id]
            children = DeckRepository.get_child_decks(node, user)

            for child in children:
                ids.extend(dfs(child))

            return ids

        return dfs(deck)

    # =========================
    # DECK DETAIL (info + stats)
    # =========================
    @staticmethod
    def get_deck_detail(deck_id, user):
        deck = DeckService._get_deck_or_404(deck_id, user)
        today = timezone.localdate()

        all_deck_ids = DeckService.get_descendant_ids(deck, user)

        # Count new cards already started today
        new_already_started_today = CardRepository.count_started_new_today(
            all_deck_ids,
            user,
            today,
        )

        NEW_LIMIT_PER_DAY = 20
        remaining_new_quota = max(0, NEW_LIMIT_PER_DAY - new_already_started_today)

        # Get cards + progress
        cards = CardRepository.get_cards_by_deck_ids(all_deck_ids)
        progress_dict = CardRepository.get_progress_dict(cards, user)

        # Build today's session counts
        session_new_count = 0
        session_learning_count = 0
        session_review_count = 0

        for card in cards:
            p = progress_dict.get(card.id)
            if not p:
                if session_new_count < remaining_new_quota:
                    session_new_count += 1
            elif p.next_review <= today:
                if p.status == "learning":
                    session_learning_count += 1
                elif p.status == "review":
                    session_review_count += 1

        # Overall stats
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

        return {
            "deck_id": deck.id,
            "name": deck.name,
            "description": deck.description,
            "counts": {
                "new": session_new_count,
                "learning": session_learning_count,
                "review": session_review_count,
                "total": session_new_count
                + session_learning_count
                + session_review_count,
            },
            "overall_stats": {
                "total": len(cards),
                "new": overall_new,
                "learning": overall_learning,
                "review": overall_review,
                "average_ease": avg_ease,
            },
        }
