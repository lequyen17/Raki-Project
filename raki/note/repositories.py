from django.db.models import Q
from django.db import transaction
from .models import NoteType, FieldDefinition, Template


class NoteRepository:
    @staticmethod
    def get_all_visible_for_user(user):
        """Lấy danh sách NoteType hệ thống và của riêng user"""
        return (
            NoteType.objects.filter(Q(user__isnull=True) | Q(user=user))
            .prefetch_related("definitions", "templates")
            .order_by("id")
        )

    @staticmethod
    def get_by_id_and_user(note_type_id, user):
        """Lấy NoteType cụ thể và kiểm tra quyền sở hữu"""
        try:
            nt = NoteType.objects.get(id=note_type_id)
            if nt.user_id is not None and nt.user_id != user.id:
                return None
            return nt
        except NoteType.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_note_type_with_relations(user, name, definitions_data, templates_data):
        """Gom logic tạo NoteType và các bảng con vào một transaction"""
        # 1. Tạo NoteType
        note_type = NoteType.objects.create(name=name, user=user)

        # 2. Tạo FieldDefinitions
        for def_name in definitions_data:
            FieldDefinition.objects.create(note_type=note_type, name=def_name)

        # 3. Tạo Templates
        for tmpl_data in templates_data:
            front_content = tmpl_data.get("front", "")
            if tmpl_data.get("is_cloze"):
                front_content = f"<!--CLOZE_TEMPLATE-->{front_content}"

            Template.objects.create(
                note_type=note_type,
                name=tmpl_data.get("name", "Template"),
                front=front_content,
                back=tmpl_data.get("back", ""),
            )
        return note_type
