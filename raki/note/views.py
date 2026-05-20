from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from deck.repositories import DeckRepository
from note.services.main_service import NoteMainService


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def note_types_view(request):
    if request.method == "POST":
        try:
            data = NoteMainService.create_note_type(request.user, request.data)
            return Response(data, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    # GET
    data = NoteMainService.get_note_types(request.user)
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_note(request, deck_id):
    deck = DeckRepository.get_deck_for_user(deck_id, request.user)

    if not deck:
        return Response({"error": "Deck not found"}, status=404)

    try:
        data = NoteMainService.create_note(deck, request.user, request.data)
        return Response(data, status=201)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
