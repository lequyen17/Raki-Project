from django.db import models
from django.contrib.auth.models import User
from deck.models import Deck


class NoteType(models.Model):

    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_types')
    

    def __str__(self):
        return self.name


class Definition(models.Model):
    note_type_id = models.ForeignKey(NoteType, on_delete=models.CASCADE, related_name='definitions')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.note_type.name} - {self.name}"


class Template(models.Model):
    note_type_id = models.ForeignKey(NoteType, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    front = models.TextField()
    back = models.TextField()

    def __str__(self):
        return f"{self.note_type.name} - {self.name}"


class Note(models.Model):
    note_type_id = models.ForeignKey(NoteType, on_delete=models.CASCADE, related_name='notes')
    deck_id = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return f"Note {self.id}"


class Value(models.Model):
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='values')
    definition_id = models.ForeignKey(Definition, on_delete=models.CASCADE, related_name='values')
    value = models.TextField()

    def __str__(self):
        return f"{self.definition.name}: {self.value}"
# Create your models here.
