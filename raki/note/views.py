from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from note.services.note_service import NoteService
from .repositories import NoteRepository
from deck.repositories import DeckRepository
from .serializers import NoteTypeValidator, NoteCreateValidator


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def note_types_view(request):

    if request.method == "POST":

        try:
            validated_data = NoteTypeValidator.validate(request.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        name = validated_data["name"]
        definitions_data = validated_data["definitions_data"]
        templates_data = validated_data["templates_data"]
        note_type = NoteRepository.create_note_type_with_relations(
            user=request.user,
            name=name,
            definitions_data=definitions_data,
            templates_data=templates_data,
        )

        return Response(
            {
                "success": True,
                "id": note_type.id,
            },
            status=201,
        )

    # GET
    note_types = NoteRepository.get_all_visible_for_user(request.user)

    results = []

    for nt in note_types:

        results.append(
            {
                "id": nt.id,
                "name": nt.name,
                "user_id": nt.user_id,
                "definitions": [
                    {
                        "id": d.id,
                        "name": d.name,
                    }
                    for d in nt.definitions.all()
                ],
                "templates": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "is_cloze": "<!--CLOZE_TEMPLATE-->" in t.front,
                        "front": t.front.replace(
                            "<!--CLOZE_TEMPLATE-->",
                            "",
                        ),
                        "back": t.back,
                    }
                    for t in nt.templates.all()
                ],
            }
        )

    return Response({"results": results})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_note(request, deck_id):

    deck = DeckRepository.get_deck_for_user(
        deck_id,
        request.user,
    )

    if not deck:
        return Response({"error": "Deck not found"}, status=404)

    try:
        validated_data = NoteCreateValidator.validate(request.data, request.user)
    except LookupError as e:
        return Response({"error": str(e)}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

    note_type = validated_data["note_type"]
    values_data = validated_data["values_data"]

    service = NoteService()

    result = service.create_note(
        deck=deck,
        note_type=note_type,
        values_data=values_data,
    )

    return Response(
        {
            "success": True,
            "note_id": result["note"].id,
            "cards_created": result["cards_created"],
        },
        status=201,
    )
