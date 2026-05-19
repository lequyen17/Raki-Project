import re
from .repositories import NoteRepository

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


# =========================
# NOTE TYPE VALIDATOR
# =========================
class NoteTypeValidator:

    @staticmethod
    def validate(data):

        name = data.get("name")
        definitions_data = data.get("definitions", [])
        templates_data = data.get("templates", [])

        if not name:
            raise ValueError("Name is required")

        if not definitions_data:
            raise ValueError("At least one field is required")

        cleaned_definitions = []

        for d in definitions_data:

            field_name = str(d).strip()

            if not field_name:
                raise ValueError("Field names cannot be empty")

            cleaned_definitions.append(field_name)

        if len(cleaned_definitions) != len(set(cleaned_definitions)):
            raise ValueError("Field names must be unique")

        if not templates_data:
            raise ValueError("At least one template is required")

        for template in templates_data:

            template_name = template.get("name", "").strip()
            is_cloze = template.get("is_cloze", False)
            front = template.get("front", "").strip()
            back = template.get("back", "").strip()

            if not template_name:
                raise ValueError("Template name is required")

            if not front:
                raise ValueError("Front design is required")

            if not is_cloze and not back:
                raise ValueError("Back design is required")

            if not is_cloze:

                has_field_tag = re.search(FIELD_TAG_REGEX, front) or re.search(
                    FIELD_TAG_REGEX, back
                )

                if not has_field_tag:
                    raise ValueError(
                        "Normal templates must contain at least one field tag"
                    )

            if re.search(TYPE_TAG_REGEX, front):
                raise ValueError(
                    "Type in answer fields can only be added to the Back design"
                )

            if is_cloze:

                matches = re.findall(CLOZE_REGEX, front)

                if not matches:
                    raise ValueError(
                        "Cloze templates must contain at least one {{c1::...}}"
                    )

                indexes = extract_cloze_indexes(front)

                if not is_valid_cloze_sequence(indexes):
                    raise ValueError(
                        f'Template "{template_name}" has invalid cloze numbers'
                    )

        return {
            "name": name,
            "definitions_data": definitions_data,
            "templates_data": templates_data,
        }


# =========================
# NOTE CREATE VALIDATOR
# =========================
class NoteCreateValidator:

    @staticmethod
    def validate(data, user):

        note_type_id = data.get("note_type_id")
        values_data = data.get("values", {})

        if not note_type_id:
            raise ValueError("note_type_id is required")

        note_type = NoteRepository.get_by_id_and_user(
            note_type_id,
            user,
        )

        if not note_type:
            raise LookupError("NoteType not found or not authorized")

        required_definitions = {str(d.id): d for d in note_type.definitions.all()}

        for def_id, definition in required_definitions.items():

            value = values_data.get(def_id)

            if value is None or not str(value).strip():
                raise ValueError(f'Field "{definition.name}" is required')

        return {
            "note_type": note_type,
            "values_data": values_data,
        }
