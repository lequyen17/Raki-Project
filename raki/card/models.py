from django.db import models
from django.contrib.auth.models import User
from note.models import Note, Template


class Card(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='cards')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='cards')
    cloze_index = models.IntegerField(default=0)


    def __str__(self):
        return f"Card {self.id}"