from behave import given, step, then, when
from django.urls import reverse

from concerts.tests.features.steps.common import (
    create_test_artist,
    create_test_concert,
    create_test_review,
    create_test_user,
    create_test_venue,
)


@when("I request the list of {entity_type}")
def step_impl(context, entity_type):
    url = reverse(f"concerts:{entity_type}-list")
    context.response = context.client.get(url)


@when("I make a new {entity_type} with valid data")
def step_impl(context, entity_type):
    if entity_type == "concert":
        artist = create_test_artist()
        venue = create_test_venue()
        data = {
            "artist": artist.id,
            "venue": venue.id,
            "date": "2023-10-15",
            "openers": [create_test_artist("Opener 1").id, create_test_artist("Opener 2").id],
        }
        url = reverse("concerts:concert-create")
    elif entity_type == "artist":
        data = {"name": "Test Artist 2"}
        url = reverse("concerts:artist-create")
    elif entity_type == "venue":
        data = {"name": "Test Venue 2", "city": "Test City 2", "state": "IL", "country": "US"}
        url = reverse("concerts:venue-create")
    elif entity_type == "review":
        concert = create_test_concert(create_test_artist(), create_test_venue(), "2023-10-15")
        data = {"concert": concert.id, "note": "This concert was amazing!", "rating": 5}
        url = reverse("concerts:add-concert-review", kwargs={"pk": concert.id})
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")

    context.response = context.client.post(url, data=data)


@given("there is a {entity_type} in the system")
def step_impl(context, entity_type):
    if entity_type == "concert":
        artist = create_test_artist()
        venue = create_test_venue()
        context.entity = create_test_concert(artist, venue, "2023-10-15")
    elif entity_type == "artist":
        context.entity = create_test_artist()
    elif entity_type == "venue":
        context.entity = create_test_venue()
    elif entity_type == "review":
        concert = create_test_concert(create_test_artist(), create_test_venue(), "2023-10-15")
        context.entity = create_test_review(
            user=create_test_user(), concert=concert, rating=5, note="Awesome concert!"
        )


@when("I request details for that {entity_type}")
def step_impl(context, entity_type):
    if entity_type == "review":
        url = reverse("concerts:get-concert-review", kwargs={"review_id": context.entity.id})
    else:
        url = reverse(f"concerts:{entity_type}-detail", kwargs={"pk": context.entity.id})
    context.response = context.client.get(url)


@when("I attend the concert")
def step_impl(context):
    url = reverse("concerts:attend-concert", kwargs={"pk": context.entity.id})
    context.response = context.client.post(url)


@step("I have attended the concert")
def step_impl(context):
    url = reverse("concerts:attend-concert", kwargs={"pk": context.entity.id})
    context.client.post(url)


@when("I unattend the concert")
def step_impl(context):
    url = reverse("concerts:unattend-concert", kwargs={"pk": context.entity.id})
    context.response = context.client.post(url)


@when("I attempt to make a new {entity_type} with data {invalid_data}")
def step_impl(context, entity_type, invalid_data):
    data = eval(invalid_data)
    if entity_type == "concert":
        url = reverse("concerts:concert-create")
    elif entity_type == "artist":
        url = reverse("concerts:artist-create")
    elif entity_type == "venue":
        url = reverse("concerts:venue-create")
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")

    context.response = context.client.post(url, data=data)


@then("I should see form errors in the response")
def step_impl(context):
    assert "This field is required." in context.response.content.decode(), "Expected form errors, but none were found."
