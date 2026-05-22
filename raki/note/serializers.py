import re

from rest_framework import serializers

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


class NoteTemplateSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    is_cloze = serializers.BooleanField(required=False, default=False)
    front = serializers.CharField(allow_blank=True, required=False, default="")
    back = serializers.CharField(allow_blank=True, required=False, default="")


class NoteTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    definitions = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of field names, e.g. ['Front', 'Back']",
    )
    templates = NoteTemplateSerializer(many=True)

    def validate(self, attrs):
        name = attrs.get("name")
        definitions_data = attrs.get("definitions", [])
        templates_data = attrs.get("templates", [])

        if not definitions_data:
            raise serializers.ValidationError("At least one field is required")

        cleaned_definitions = []

        for d in definitions_data:
            field_name = str(d).strip()

            if not field_name:
                raise serializers.ValidationError("Field names cannot be empty")

            cleaned_definitions.append(field_name)

        if len(cleaned_definitions) != len(set(cleaned_definitions)):
            raise serializers.ValidationError("Field names must be unique")

        if not templates_data:
            raise serializers.ValidationError("At least one template is required")

        for template in templates_data:
            template_name = template.get("name", "").strip()
            is_cloze = template.get("is_cloze", False)
            front = template.get("front", "").strip()
            back = template.get("back", "").strip()

            if not template_name:
                raise serializers.ValidationError("Template name is required")

            if not front:
                raise serializers.ValidationError("Front design is required")

            if not is_cloze and not back:
                raise serializers.ValidationError("Back design is required")

            if not is_cloze:
                has_field_tag = re.search(FIELD_TAG_REGEX, front) or re.search(
                    FIELD_TAG_REGEX, back
                )

                if not has_field_tag:
                    raise serializers.ValidationError(
                        "Normal templates must contain at least one field tag like {{Front}} or {{Back}}"
                    )

            if re.search(TYPE_TAG_REGEX, front):
                raise serializers.ValidationError(
                    "Type in answer fields can only be added to the Back design"
                )

            if is_cloze:
                matches = re.findall(CLOZE_REGEX, front)

                if not matches:
                    raise serializers.ValidationError(
                        "Cloze templates must contain at least one {{c1::...}}"
                    )

                indexes = extract_cloze_indexes(front)

                if not is_valid_cloze_sequence(indexes):
                    raise serializers.ValidationError(
                        f'Template "{template_name}" has invalid cloze numbers'
                    )

        return {
            "name": name,
            "definitions_data": definitions_data,
            "templates_data": templates_data,
        }


class NoteValueSerializer(serializers.Serializer):
    # Định nghĩa cấu trúc cho từng item trong list
    def_id = serializers.IntegerField(required=True)
    value = serializers.CharField(allow_blank=False, required=True)


class NoteCreateSerializer(serializers.Serializer):
    note_type_id = serializers.IntegerField()
    values = NoteValueSerializer(many=True)  # Chấp nhận một danh sách các object

    def validate(self, attrs):
        user = self.context["user"]
        note_type_id = attrs.get("note_type_id")
        values_list = attrs.get("values", [])

        # 1. Kiểm tra NoteType
        note_type = NoteRepository.get_by_id_and_user(note_type_id, user)
        if not note_type:
            raise serializers.ValidationError(
                {"note_type_id": "NoteType not found or not authorized"}
            )

        # 2. Chuyển list gửi lên thành dict để dễ truy xuất: {def_id: value}
        # Ví dụ: [{"def_id": "1", "value": "A"}] -> {"1": "A"}
        input_data = {item["def_id"]: item["value"] for item in values_list}

        # 3. Lấy các định nghĩa bắt buộc từ Database
        required_definitions = note_type.definitions.all()

        for definition in required_definitions:

            value = input_data.get(definition.id)

            # Kiểm tra nếu thiếu field hoặc field rỗng
            if value is None or not str(value).strip():
                raise serializers.ValidationError(
                    f'Field "{definition.name}" (ID: {definition.id}) is required'
                )

        # Trả về dữ liệu đã qua xử lý
        return {
            "note_type": note_type,
            "values_data": input_data,  # Trả về dạng dict cho logic phía sau dễ dùng
        }


# --- OpenAPI response schemas ---


class NoteTypeDefinitionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class NoteTypeTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_cloze = serializers.BooleanField()
    front = serializers.CharField()
    back = serializers.CharField()


class NoteTypeItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    user_id = serializers.IntegerField(allow_null=True)
    definitions = NoteTypeDefinitionSerializer(many=True)
    templates = NoteTypeTemplateSerializer(many=True)


class NoteTypeListResponseSerializer(serializers.Serializer):
    results = NoteTypeItemSerializer(many=True)


class NoteTypeCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    id = serializers.IntegerField()


class NoteCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    note_id = serializers.IntegerField()
    cards_created = serializers.IntegerField()
