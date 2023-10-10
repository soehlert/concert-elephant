import json

from behave import step, then, when
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from concerts.models import Artist, Concert, ConcertReview, Venue
from concerts.tests.features.steps.common import create_test_artist, create_test_concert, create_test_venue

url_map = {
    "artist": "api:v1:artist-list",
    "concert": "api:v1:concert-list",
    "venue": "api:v1:venue-list",
    "review": "api:v1:concertreview-list",
}

model_map = {"artist": Artist, "concert": Concert, "venue": Venue, "review": ConcertReview}


@when("I request the {entity} list")
def step_impl(context, entity):
    # Ensure that the provided entity name is recognized
    if entity not in url_map:
        raise ValueError(f"Unknown entity name: {entity}")

    # Use the url_map to get the correct URL pattern for the entities
    url = reverse(url_map[entity])

    # Make the GET request
    headers = getattr(context, "headers", {})
    response = context.client.get(url, **headers)
    context.response = response


@when("I create a new {entity_type} with {data}")
def step_impl(context, entity_type, data):
    data = json.loads(data)

    if entity_type not in url_map:
        raise ValueError(f"Invalid entity_type: {entity_type}")

    if entity_type == "concert":
        artist_url = reverse("api:v1:artist-detail", args=[context.last_artist_id])
        venue_url = reverse("api:v1:venue-detail", args=[context.last_venue_id])
        data["artist"] = artist_url
        data["venue"] = venue_url

    elif entity_type == "review":
        concert_url = reverse("api:v1:concert-detail", args=[context.last_concert_id])
        data["concert"] = concert_url

    url = reverse(url_map[entity_type])
    context.response = context.client.post(url, data, format="json")

    if context.response.status_code == 201:
        created_data = context.response.json()
        if entity_type == "artist":
            context.last_artist_id = created_data["id"]
        elif entity_type == "venue":
            context.last_venue_id = created_data["id"]
        elif entity_type == "concert":
            context.last_concert_id = created_data["id"]
    elif context.response.status_code == 400:
        error_msg = json.dumps(context.response.json(), indent=4)  # Format the entire JSON response
        raise AssertionError(f"API returned 400 Bad Request:\n{error_msg}")


@then("I should receive a list of entities")
def step_impl(context):
    assert context.response.status_code == 200
    assert isinstance(context.response.json(), list)


@then("The {entity_type} should be added to the database")
def step_impl(context, entity_type):
    assert model_map[entity_type].objects.count() > 0, f"{entity_type.capitalize()} was not added to the database."


@step("{user} has created {num:d} concert reviews")
def step_impl(context, user, num):
    for _ in range(num):
        artist = create_test_artist(name=f"test artist {_ + 1}")
        venue = create_test_venue(name=f"test venue {_ + 1}")
        concert = create_test_concert(artist, venue, timezone.now())
        ConcertReview.objects.create(user=context.user, concert=concert, rating=5, note=f"Review {_ + 1}")


@then("the response should contain an empty list of reviews")
def step_impl(context):
    assert len(context.response.data) == 0, f"Expected empty list but got {len(context.response.data)} reviews"


@when("{user} requests the list of concert reviews for {author}")
def step_impl(context, user, author):
    # Ensure the context user is set to the requesting user
    context.user = get_user_model().objects.get(username=user)
    url = reverse("api:v1:concertreview-list")
    context.client.force_authenticate(context.user)
    context.response = context.client.get(url)


@then("I should receive a list of {num:d} reviews")
def step_impl(context, num):
    assert len(context.response.json()) == num


@step("{user} has created a concert review with note {text} and the rating {score}")
def step_impl(context, user, text, score):
    artist = create_test_artist()
    venue = create_test_venue()
    concert = create_test_concert(artist, venue, timezone.now())
    review = ConcertReview.objects.create(concert=concert, user=context.user, rating=score, note=text)
    context.review = review


@when("I update the concert review with note {text}")
def step_impl(context, text):
    url = reverse("api:v1:concertreview-detail", args=[context.review.id])
    data = {"note": text, "rating": 2}
    context.client.force_authenticate(context.user)
    context.response = context.client.patch(url, data, format="json")


@when("{user} tries to update the concert review created by {author} with note {text}")
def step_impl(context, user, author, text):
    url = reverse("api:v1:concertreview-detail", args=[context.review.id])
    data = {"note": text}
    context.client.force_authenticate(context.user)
    context.response = context.client.patch(url, data, format="json")


@when("I delete the concert review")
def step_impl(context):
    url = reverse("api:v1:concertreview-detail", args=[context.review.id])
    context.client.force_authenticate(context.user)
    context.response = context.client.delete(url)


@then("The concert review should be removed from the database")
def step_impl(context):
    assert not ConcertReview.objects.filter(id=context.review.id).exists()


@when("I try to delete the concert review created by {user}")
def step_impl(context, user):
    url = reverse("api:v1:concertreview-detail", args=[context.review.id])
    context.response = context.client.delete(url)


@then("The concert review should be updated to {note}")
def step_impl(context, note):
    updated_review = ConcertReview.objects.get(id=context.review.id)
    assert updated_review.note == note
