import random
from datetime import datetime, timedelta

import factory
from factory import Faker, LazyFunction, SubFactory

from concert_elephant.users.tests.factories import UserFactory
from concerts.models import Artist, Concert, ConcertReview, Venue


class ArtistFactory(factory.django.DjangoModelFactory):
    name = Faker("name")

    class Meta:
        model = Artist
        django_get_or_create = ["name"]


class VenueFactory(factory.django.DjangoModelFactory):
    name = Faker("street_name")
    city = Faker("city")
    country = Faker("country_code")

    class Meta:
        model = Venue
        django_get_or_create = ["name", "city"]


class ConcertFactory(factory.django.DjangoModelFactory):
    artist = SubFactory(ArtistFactory)
    venue = SubFactory(VenueFactory)

    class Meta:
        model = Concert

    @staticmethod
    def random_date_within_past_year():
        return datetime.now() - timedelta(days=random.randint(0, 365))

    date = LazyFunction(random_date_within_past_year)

    @factory.post_generation
    def opener(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for artist in extracted:
                self.opener.add(artist)
        else:
            self.opener.add(ArtistFactory())


class ConcertReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConcertReview

    user = SubFactory(UserFactory)
    concert = SubFactory(ConcertFactory)
    rating = Faker("random_int", min=1, max=5)
    note = Faker("sentence")
