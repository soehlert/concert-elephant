from behave import given
from django.contrib.auth import get_user_model

from concerts.models import Artist, Concert, ConcertReview, Venue


def create_test_user(username):
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username)

    if created:
        user.set_password("testpassword")
        user.save()

    return user


def create_test_artist():
    return Artist.objects.create(name="Test Artist")


def create_test_venue():
    return Venue.objects.create(name="Test Venue", city="Chicago")


def create_test_concert(date):
    return Concert.objects.create(artist=create_test_artist(), venue=create_test_venue(), date=date)


def create_test_review(user, concert, rating, note):
    return ConcertReview.objects.create(user=user, concert=concert, rating=rating, note=note)


@given('I have a registered user "{username}"')
def step_impl(context, username):  # noqa: F811
    user = create_test_user(username)
    context.user = user


@given('"{username}" is logged in')
def step_impl(context, username):  # noqa: F811
    context.test.client.login(username=username, password="testpassword")
    if not context.test.client.login(username=username, password="testpassword"):
        raise AssertionError(f"Failed to log in as {username}")


def after_scenario(context, scenario):
    User = get_user_model()
    User.objects.all().delete()
    Artist.objects.all().delete()
    Concert.objects.all().delete()
    ConcertReview.objects.all().delete()
