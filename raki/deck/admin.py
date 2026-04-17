from django.contrib import admin
from .models import Deck,UserDeck

admin.site.register([Deck,UserDeck])
