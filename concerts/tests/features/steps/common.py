from behave import given, then
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from concerts.models import Artist, Concert, ConcertReview, Venue


def create_test_user(username="testuser"):
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username)

    if created:
        user.set_password("testpassword")
        user.save()

    return user


def create_test_artist(name="Test Artist"):
    return Artist.objects.create(name=name)


def create_test_venue(name="Test Venue", city="Test City"):
    return Venue.objects.create(name=name, city=city)


def create_test_concert(artist, venue, date):
    return Concert.objects.create(artist=artist, venue=venue, date=date)


def create_test_review(user, concert, rating=3, note="Test Note"):
    return ConcertReview.objects.create(user=user, concert=concert, rating=rating, note=note)


@given("I am an unauthenticated user")
def step_impl(context):
    context.client.logout()


@given("I am an anonymous user")
def step_impl(context):
    context.user = None


@given("I have a registered user {username}")
def step_impl(context, username):
    context.user = create_test_user(username)


@given("{username} is logged in")
def step_impl(context, username):
    context.client.login(username=username, password="testpassword")
    if not context.client.login(username=username, password="testpassword"):
        raise AssertionError(f"Failed to log in as {username}")


@given("I am a token authenticated user {username}")
def step_impl(context, username):
    User = get_user_model()
    user = User.objects.get(username=username)
    token, _ = Token.objects.get_or_create(user=user)

    # Authenticate using the DRF client's authentication mechanism
    context.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)


@then("the response status code should be {status_code:d}")
def step_impl(context, status_code):
    assert context.response.status_code == int(
        status_code
    ), f"Expected {status_code} but got {context.response.status_code}"


def after_scenario(context, _):
    User = get_user_model()
    User.objects.exclude(username="testuser").delete()
    Artist.objects.all().delete()
    Concert.objects.all().delete()
    ConcertReview.objects.all().delete()
