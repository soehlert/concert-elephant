from django.core.management.base import BaseCommand
from titlecase import titlecase

from concerts.models import Artist
from concerts.tests.constants import REAL_ARTIST_NAMES
from concerts.tests.factories import ArtistFactory, ConcertFactory, ConcertReviewFactory, UserFactory, VenueFactory


class Command(BaseCommand):
    help = "Generate test data for the app"

    def handle(self, *args, **kwargs):
        # There's 50 names on this list
        existing_artist_names = Artist.objects.values_list("name", flat=True)

        for artist in REAL_ARTIST_NAMES:
            titlecased_artist = titlecase(artist)
            if titlecased_artist.strip() == "":
                print("Found an empty or whitespace-only artist name.")
                continue

            if titlecased_artist not in existing_artist_names:
                ArtistFactory.create(name=titlecased_artist)

        try:
            VenueFactory.create_batch(50)
        except Exception as e:
            print("Error creating venue:", e)

        ConcertFactory.create_batch(50)
        UserFactory.create_batch(5)
        ConcertReviewFactory.create_batch(25)
        self.stdout.write(self.style.SUCCESS("Successfully generated test data"))
