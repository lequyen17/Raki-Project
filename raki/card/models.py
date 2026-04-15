from django.db import models
from django.contrib.auth.models import User
from note.models import Note, Template


class Card(models.Model):
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='cards')
    template_id = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='cards')

    # Spaced repetition
    next_review = models.DateTimeField(db_index=True)
    easiness = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    repetition = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Card {self.id}"