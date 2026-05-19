from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from note.services.note_service import NoteService
from .repositories import NoteRepository
from deck.repositories import DeckRepository

import re

FIELD_TAG_REGEX = r"\{\{[^}]+\}\}"
TYPE_TAG_REGEX = r"\{\{type:[^}]+\}\}"
CLOZE_REGEX = r"\{\{c(\d+)::.+?\}\}"


def extract_cloze_indexes(text):
    return [int(x) for x in re.findall(CLOZE_REGEX, text)]


def is_valid_cloze_sequence(indexes):
    if not indexes:
        return True

    unique_sorted = sorted(set(indexes))

    return unique_sorted == list(range(1, max(unique_sorted) + 1))


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def note_types_view(request):

    if request.method == "POST":

        name = request.data.get("name")
        definitions_data = request.data.get("definitions", [])
        templates_data = request.data.get("templates", [])

        # =====================
        # Note type validate
        # =====================

        if not name:
            return Response(
                {"error": "Name is required"},
                status=400,
            )

        # =====================
        # Definitions validate
        # =====================

        if not definitions_data:
            return Response(
                {"error": "At least one field is required"},
                status=400,
            )

        cleaned_definitions = []

        for d in definitions_data:

            field_name = str(d).strip()

            if not field_name:
                return Response(
                    {"error": "Field names cannot be empty"},
                    status=400,
                )

            cleaned_definitions.append(field_name)

        # duplicate field names
        if len(cleaned_definitions) != len(set(cleaned_definitions)):
            return Response(
                {"error": "Field names must be unique"},
                status=400,
            )

        # =====================
        # Templates validate
        # =====================

        if not templates_data:
            return Response(
                {"error": "At least one template is required"},
                status=400,
            )

        for template in templates_data:

            template_name = template.get("name", "").strip()
            is_cloze = template.get("is_cloze", False)
            front = template.get("front", "").strip()
            back = template.get("back", "").strip()

            # required fields
            if not template_name:
                return Response(
                    {"error": "Template name is required"},
                    status=400,
                )

            if not front:
                return Response(
                    {"error": "Front design is required"},
                    status=400,
                )

            if not is_cloze and not back:
                return Response(
                    {"error": "Back design is required"},
                    status=400,
                )

            # =====================
            # Normal template validate
            # =====================

            if not is_cloze:

                has_field_tag = re.search(FIELD_TAG_REGEX, front) or re.search(
                    FIELD_TAG_REGEX, back
                )

                if not has_field_tag:
                    return Response(
                        {
                            "error": (
                                "Normal templates must contain "
                                "at least one field tag"
                            )
                        },
                        status=400,
                    )

            # =====================
            # type: field validate
            # =====================

            if re.search(TYPE_TAG_REGEX, front):
                return Response(
                    {
                        "error": (
                            "Type in answer fields "
                            "can only be added to the Back design"
                        )
                    },
                    status=400,
                )

            # =====================
            # Cloze validate
            # =====================

            if is_cloze:

                matches = re.findall(CLOZE_REGEX, front)

                if not matches:
                    return Response(
                        {
                            "error": (
                                "Cloze templates must contain "
                                "at least one {{c1::...}}"
                            )
                        },
                        status=400,
                    )

                indexes = extract_cloze_indexes(front)

                if not is_valid_cloze_sequence(indexes):
                    return Response(
                        {
                            "error": (
                                f'Template "{template_name}" '
                                "has invalid cloze numbers"
                            )
                        },
                        status=400,
                    )

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

    note_type_id = request.data.get("note_type_id")

    values_data = request.data.get("values", {})

    if not note_type_id:
        return Response(
            {"error": "note_type_id is required"},
            status=400,
        )

    note_type = NoteRepository.get_by_id_and_user(
        note_type_id,
        request.user,
    )

    if not note_type:
        return Response(
            {"error": "NoteType not found or not authorized"},
            status=404,
        )

    required_definition_ids = {str(d.id): d for d in note_type.definitions.all()}

    # empty check
    for def_id, definition in required_definition_ids.items():

        value = values_data.get(def_id)

        if value is None or not str(value).strip():
            return Response(
                {"error": f'Field "{definition.name}" is required'},
                status=400,
            )

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
