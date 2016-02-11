from django.contrib import admin

# Register your models here.
from .models.bible import Bible
from .models.subscribers import Subscribers
from .models.wordstats import WordStats
from .models.bookstats import BookStats


admin.site.register(Bible)
admin.site.register(Subscribers)
admin.site.register(WordStats)
admin.site.register(BookStats)
