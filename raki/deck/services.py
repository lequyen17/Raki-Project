from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from deck.repositories import DeckRepository
from card.repositories import CardRepository
from deck.models import Deck, UserDeck
from card.models import Card, Progress
from payment.models import CoinHistory, CoinTransaction
from payment.repositories import WalletRepository

User = get_user_model()


class DeckService:

    @staticmethod
    def _get_deck_or_404(deck_id, user):
        deck = DeckRepository.get_deck_for_user(deck_id, user)
        if not deck:
            raise LookupError("DECK_NOT_FOUND")
        return deck

    @staticmethod
    def _get_deck_for_owner_or_404(deck_id, user):
        deck = DeckRepository.get_deck_for_owner(deck_id, user)
        if not deck:
            raise LookupError("DECK_NOT_FOUND_OR_NOT_OWNER")
        return deck

    @staticmethod
    def _serialize_collaborators(deck):
        return [
            {
                "user_id": ud.user_id,
                "username": ud.user.username,
                "role": ud.role,
            }
            for ud in DeckRepository.get_collaborators(deck)
        ]

    @staticmethod
    def _build_share_settings(deck):
        coin_price = deck.coin_price or 0
        return {
            "share_mode": deck.share_mode or "private",
            "coin_price": coin_price,
            "access_type": "premium" if coin_price > 0 else "free",
            "collaborators": DeckService._serialize_collaborators(deck),
        }

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
            "share_mode": deck.share_mode or "private",
            "coin_price": deck.coin_price or 0,
            "parent_id": deck.parent_id,
            "created_at": deck.created_at,
        }

    # =========================
    # GET ALL USER DECKS
    # =========================
    @staticmethod
    def get_user_decks(user):
        decks = DeckRepository.get_user_decks(user)
        user_decks = UserDeck.objects.filter(user=user)
        role_map = {ud.deck_id: ud.role for ud in user_decks}

        results = []
        for deck in decks:
            results.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description or "",
                    "coin_price": deck.coin_price or 0,
                    "share_mode": deck.share_mode or "private",
                    "total_cards": deck.total_cards,
                    "parent_id": deck.parent_id,
                    "created_at": deck.created_at,
                    "role": role_map.get(deck.id, "viewer"),
                }
            )
        return {
            "count": decks.count(),
            "results": results,
        }

    # =========================
    # GET PUBLIC DECKS
    # =========================
    @staticmethod
    def get_public_decks(user):
        decks = DeckRepository.get_public_decks()
        user_decks = UserDeck.objects.filter(user=user, deck__in=decks)
        role_map = {ud.deck_id: ud.role for ud in user_decks}

        results = []
        for deck in decks:
            owner = deck.deck_users.filter(role="owner").first()
            owner_name = owner.user.username if owner else "Unknown"

            results.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description or "",
                    "coin_price": deck.coin_price or 0,
                    "share_mode": deck.share_mode or "public",
                    "parent_id": deck.parent_id,
                    "created_at": deck.created_at,
                    "owner": owner_name,
                    "role": role_map.get(deck.id, "none"),
                }
            )
        return {
            "count": decks.count(),
            "results": results,
        }

    # =========================
    # LEARN PUBLIC DECK
    # =========================
    @staticmethod
    def learn_public_deck(deck_id, user):

        # Lấy deck công khai
        deck = Deck.objects.filter(id=deck_id, share_mode="public").first()
        if not deck:
            raise LookupError("DECK_NOT_FOUND_OR_NOT_PUBLIC")

        if UserDeck.objects.filter(user=user, deck=deck).exists():
            return {"success": False, "message": "Already learning this deck"}

        all_decks_to_learn = DeckRepository.get_all_descendants(deck)

        coin_price = deck.coin_price or 0
        if coin_price > 0 and not CoinTransaction.objects.filter(
            deck=deck, buyer=user
        ).exists():
            balance = WalletRepository.get_coin_balance(user)
            if balance < coin_price:
                return {"success": False, "error": "INSUFFICIENT_COINS"}

            owner_ud = deck.deck_users.filter(role="owner").select_related("user").first()
            if not owner_ud:
                raise LookupError("DECK_OWNER_NOT_FOUND")

            net_coin = coin_price * 90 // 100
            commission_coin = coin_price - net_coin

            with transaction.atomic():
                buyer_profile = user.profile
                buyer_profile.coin_balance -= coin_price
                buyer_profile.save(update_fields=["coin_balance"])

                owner_profile = owner_ud.user.profile
                owner_profile.coin_balance += net_coin
                owner_profile.save(update_fields=["coin_balance"])

                CoinHistory.objects.create(
                    user=user, amount=-coin_price, reason="BUY_DECK"
                )
                CoinHistory.objects.create(
                    user=owner_ud.user, amount=net_coin, reason="SELL_DECK"
                )
                CoinTransaction.objects.create(
                    deck=deck,
                    buyer=user,
                    gross_coin=coin_price,
                    commission_coin=commission_coin,
                    net_coin=net_coin,
                )

        user_decks = []
        for d in all_decks_to_learn:
            user_decks.append(UserDeck(user=user, deck=d, role="viewer"))
        UserDeck.objects.bulk_create(user_decks, ignore_conflicts=True)

        return {"success": True}

    # =========================
    # UNLEARN (remove viewer role)
    # =========================
    @staticmethod
    def unlearn_deck(deck_id, user):
        user_deck = UserDeck.objects.filter(
            user=user, deck_id=deck_id, role="viewer"
        ).first()
        if not user_deck:
            raise LookupError("DECK_NOT_FOUND_OR_NOT_VIEWER")

        deck = user_deck.deck

        def get_all_descendants(node):
            descendants = [node]
            for child in Deck.objects.filter(parent=node):
                descendants.extend(get_all_descendants(child))
            return descendants

        deck_ids = [d.id for d in get_all_descendants(deck)]
        UserDeck.objects.filter(user=user, deck_id__in=deck_ids, role="viewer").delete()

        return {"success": True}

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
            "share_mode": deck.share_mode or "private",
            "coin_price": deck.coin_price or 0,
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
        deck = DeckService._get_deck_for_owner_or_404(deck_id, user)
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
        user_deck = UserDeck.objects.filter(user=user, deck=deck).first()
        role = user_deck.role if user_deck else "none"

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
            "coin_price": deck.coin_price or 0,
            "share_mode": deck.share_mode or "private",
            "role": role,
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

    # =========================
    # SHARE SETTINGS
    # =========================
    @staticmethod
    def get_share_settings(deck_id, user):
        deck = DeckService._get_deck_for_owner_or_404(deck_id, user)
        return DeckService._build_share_settings(deck)

    @staticmethod
    def update_share_settings(deck_id, user, validated_data):
        deck = DeckService._get_deck_for_owner_or_404(deck_id, user)
        share_mode = validated_data["share_mode"]
        coin_price = validated_data.get("coin_price", 0)

        if share_mode == "private":
            DeckRepository.update_deck_share(
                deck, share_mode="private", coin_price=0
            )
            DeckRepository.remove_non_owner_members(deck)
        elif share_mode == "public":
            if coin_price < 0:
                raise ValueError("INVALID_COIN_PRICE")
            DeckRepository.update_deck_share(
                deck, share_mode="public", coin_price=coin_price
            )
        elif share_mode == "restricted":
            DeckRepository.update_deck_share(
                deck, share_mode="restricted", coin_price=0
            )

        return DeckService._build_share_settings(deck)

    @staticmethod
    def add_collaborator(deck_id, user, validated_data):
        deck = DeckService._get_deck_for_owner_or_404(deck_id, user)
        username = validated_data["username"]
        role = validated_data["role"]

        target_user = User.objects.filter(username=username).first()
        if not target_user:
            raise LookupError("USER_NOT_FOUND")
        if target_user.id == user.id:
            raise ValueError("CANNOT_SHARE_WITH_SELF")

        if deck.share_mode != "restricted":
            DeckRepository.update_deck_share(
                deck, share_mode="restricted", coin_price=0
            )

        all_decks = DeckRepository.get_all_descendants(deck)
        for d in all_decks:
            existing = UserDeck.objects.filter(user=target_user, deck=d).first()
            if existing:
                if existing.role == "owner":
                    raise ValueError("USER_ALREADY_OWNER")
                existing.role = role
                existing.save(update_fields=["role"])
            else:
                UserDeck.objects.create(user=target_user, deck=d, role=role)

        return DeckService._build_share_settings(deck)

    @staticmethod
    def remove_collaborator(deck_id, user, target_user_id):
        deck = DeckService._get_deck_for_owner_or_404(deck_id, user)
        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            raise LookupError("USER_NOT_FOUND")

        all_decks = DeckRepository.get_all_descendants(deck)
        deck_ids = [d.id for d in all_decks]
        deleted, _ = UserDeck.objects.filter(
            user=target_user,
            deck_id__in=deck_ids,
        ).exclude(role="owner").delete()

        if deleted == 0:
            raise LookupError("COLLABORATOR_NOT_FOUND")

        return DeckService._build_share_settings(deck)

    @staticmethod
    def search_users(query, user):
        keyword = (query or "").strip()
        if len(keyword) < 2:
            return {"results": []}

        users = DeckRepository.search_users(keyword, user)
        return {
            "results": [
                {"id": u.id, "username": u.username}
                for u in users
            ]
        }
