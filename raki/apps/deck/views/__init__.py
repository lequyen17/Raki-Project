from apps.deck.views.decks import MoveUserDeckView, UserDecksView
from apps.deck.views.deck_detail import UserDeckDetailView
from apps.deck.views.public import LearnPublicDeckView, PublicDecksView, UnlearnDeckView
from apps.deck.views.share import (
    DeckAddCollaboratorView,
    DeckRemoveCollaboratorView,
    DeckShareSettingsView,
)
from apps.deck.views.search import SearchUsersView

__all__ = [
    "UserDecksView",
    "MoveUserDeckView",
    "UserDeckDetailView",
    "PublicDecksView",
    "LearnPublicDeckView",
    "UnlearnDeckView",
    "DeckShareSettingsView",
    "DeckAddCollaboratorView",
    "DeckRemoveCollaboratorView",
    "SearchUsersView",
]
