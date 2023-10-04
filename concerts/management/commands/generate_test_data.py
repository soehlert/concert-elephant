from django.core.management.base import BaseCommand

from concerts.tests.factories import ArtistFactory, ConcertFactory, ConcertReviewFactory, UserFactory, VenueFactory


class Command(BaseCommand):
    help = "Generate test data for the app"

    def handle(self, *args, **kwargs):
        ArtistFactory.create_batch(50)
        VenueFactory.create_batch(50)
        ConcertFactory.create_batch(50)
        UserFactory.create_batch(5)
        ConcertReviewFactory.create_batch(25)
        self.stdout.write(self.style.SUCCESS("Successfully generated test data"))
