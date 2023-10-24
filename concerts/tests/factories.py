import random
from datetime import datetime, timedelta

import factory
from factory import Faker, LazyFunction, SubFactory

from concert_elephant.users.tests.factories import UserFactory
from concerts.models import Artist, Concert, ConcertReview, Venue


class ArtistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Artist


class VenueFactory(factory.django.DjangoModelFactory):
    name = Faker("street_name")
    city = Faker("city")
    state = Faker("state_abbr")
    country = Faker("country_code", representation="alpha-2")

    class Meta:
        model = Venue
        django_get_or_create = ["name", "city", "state"]


class ConcertFactory(factory.django.DjangoModelFactory):
    venue = SubFactory(VenueFactory)

    class Meta:
        model = Concert

    @staticmethod
    def random_date_within_past_year():
        return datetime.now() - timedelta(days=random.randint(0, 365))

    date = LazyFunction(random_date_within_past_year)

    @factory.lazy_attribute
    def artist(self):
        artists = Artist.objects.all()
        if artists.exists():
            return random.choice(artists)

    @factory.post_generation
    def opener(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            # If opener artists are explicitly provided, use them
            for artist in extracted:
                self.opener.add(artist)
        else:
            # Otherwise, choose a random artist from the database
            artists = Artist.objects.exclude(id=self.artist.id).all()
            if artists.exists():
                self.opener.add(random.choice(artists))


class ConcertReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConcertReview

    user = SubFactory(UserFactory)
    concert = SubFactory(ConcertFactory)
    rating = Faker("random_int", min=1, max=5)
    note = Faker("sentence")
