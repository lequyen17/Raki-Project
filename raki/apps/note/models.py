from django.db import models
from django.contrib.auth.models import User
from apps.deck.models import Deck


class NoteType(models.Model):

    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="note_types", null=True, blank=True
    )

    def __str__(self):
        return self.name


class FieldDefinition(models.Model):
    note_type = models.ForeignKey(
        NoteType, on_delete=models.CASCADE, related_name="definitions"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.note_type.name} - {self.name}"


class Template(models.Model):
    note_type = models.ForeignKey(
        NoteType, on_delete=models.CASCADE, related_name="templates"
    )
    name = models.CharField(max_length=100)
    front = models.TextField()
    back = models.TextField()

    def __str__(self):
        return f"{self.note_type.name} - {self.name}"


class Note(models.Model):
    note_type = models.ForeignKey(
        NoteType, on_delete=models.CASCADE, related_name="notes"
    )
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="notes")

    def __str__(self):
        return f"Note {self.id}"


class FieldValue(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="values")
    definition = models.ForeignKey(
        FieldDefinition, on_delete=models.CASCADE, related_name="values"
    )
    value = models.TextField()

    def __str__(self):
        return f"{self.definition.name}: {self.value}"


# Create your models here.
