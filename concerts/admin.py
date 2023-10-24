from django.contrib import admin

from .models import Artist, Concert, ConcertReview, Venue


# Register your models here.
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "musicbrainz_id", "processed_for_musicbrainz")
    search_fields = ("artist",)


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Concert)
admin.site.register(ConcertReview)
admin.site.register(Venue)
