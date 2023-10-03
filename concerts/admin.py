from django.contrib import admin

from .models import Artist, Concert, ConcertReview, Venue

# Register your models here.

admin.site.register(Artist)
admin.site.register(Concert)
admin.site.register(ConcertReview)
admin.site.register(Venue)
