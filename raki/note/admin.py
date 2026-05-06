from django.contrib import admin
from .models import FieldDefinition, Note, NoteType, FieldValue, Template

admin.site.register([FieldDefinition, Note, NoteType, FieldValue, Template]) # Đăng ký gộp một danh sách luôn cho gọn