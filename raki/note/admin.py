from django.contrib import admin
from .models import Definition, Note, NoteType, Value, Template

admin.site.register([Definition, Note, NoteType, Value, Template]) # Đăng ký gộp một danh sách luôn cho gọn