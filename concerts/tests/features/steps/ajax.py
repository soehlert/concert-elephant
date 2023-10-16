import json
import logging

from behave import given, then, when
from django.test import Client
from django.urls import reverse

from concerts.models import Artist, Venue
from concerts.tests.features.steps.common import create_test_artist, create_test_concert, create_test_venue

logger = logging.getLogger(__name__)


@given('a {entity} named "{name}"')
def step_impl(context, entity, name):
    logger.info(f"Creating {entity}: {name}")
    if entity == "artist" or entity == "opener":
        Artist.objects.create(name=name)
    elif entity == "venue":
        Venue.objects.create(name=name)
    else:
        error_message = f"Unsupported entity '{entity}'. Supported entities are 'artist', 'opener', and 'venue'."
        logger.error(error_message)
        raise AssertionError(error_message)


@when('I search for a {model} with the term "{term}" using the "{url_name}" URL')
def step_impl(context, model, term, url_name):
    url = reverse(f"concerts:{url_name}")
    context.response = Client().get(url, {"term": term})


@then('I should receive a response containing "{expected}"')
def step_impl(context, expected):
    # Decode the byte-string to string and load into a dictionary
    response_data = json.loads(context.response.content.decode("utf-8"))

    # Assuming the response is a list of dictionaries, and we are searching in the 'label' key
    labels = [item["label"] for item in response_data if "label" in item]

    # Assert that the expected value is in the labels
    assert any(expected in label for label in labels), f"Expected '{expected}' not found in response labels: {labels}"


@given('an artist named "{name}"')
def step_impl(context, name):
    Artist.objects.create(name=name)


@when('I make an AJAX request to the detail page of artist "{name}"')
def step_impl(context, name):
    artist = Artist.objects.get(name=name)
    url = reverse("concerts:artist-detail", args=[artist.id])
    context.response = Client().get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    logger.info("Made AJAX request for detail page")


@then('I should receive a JSON response containing the name "{name}"')
def step_impl(context, name):
    response_data = json.loads(context.response.content)
    assert response_data.get("name") == name


@when('I submit the artist creation form with name "{name}" using AJAX')
def step_impl(context, name):
    url = reverse("concerts:artist-create")
    context.response = context.client.post(url, {"name": name}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")


@then("I should receive a JSON response indicating success")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected status code 200 but got {context.response.status_code}"
    assert (
        context.response["Content-Type"] == "application/json"
    ), f"Expected 'application/json' but got {context.response['Content-Type']}"

    response_content = context.response.content.decode("utf-8")
    assert response_content, "Response content is empty"

    response_data = json.loads(response_content)
    assert response_data.get("status") == "success", f"Actual status: '{response_data.get('status')}'"


@then('the response should contain the artist id and name "{name}"')
def step_impl(context, name):
    response_data = json.loads(context.response.content)
    assert "artistId" in response_data, "artistId not found in response"
    assert response_data.get("artist") == name, f"Actual artist name: '{response_data.get('artist')}'"


@when('I submit the venue creation form with name "{name}", city "{city}", and country "{country}" using AJAX')
def step_impl(context, name, city, country):
    url = reverse("concerts:venue-create")
    context.response = context.client.post(
        url, {"name": name, "city": city, "country": country}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )


@then('the response should contain the venue id, name "{name}", city "{city}", and country "{country}"')
def step_impl(context, name, city, country):
    response_json = json.loads(context.response.content)
    venue = response_json["venue"]
    assert venue["name"] == name, f"Expected venue name '{name}', but got '{venue['name']}'"
    assert venue["city"] == city, f"Expected venue city '{city}', but got '{venue['city']}'"
    assert venue["country"] == country, f"Expected venue country '{country}', but got '{venue['country']}'"


@when("I request the concert list using AJAX")
def step_impl(context):
    url = reverse("concerts:concert-list")
    context.response = context.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")


@then("I should receive a JSON response containing the concert list")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected status code 200, but got {context.response.status_code}"
    response_json = json.loads(context.response.content)
    assert "concerts" in response_json, "Response JSON does not contain 'concerts'"


@given("a concert exists")
def step_impl(context):
    artist = create_test_artist()
    venue = create_test_venue()
    concert = create_test_concert(artist, venue, "2023-01-01")  # Adjust the date as needed
    context.concert_id = concert.id


@when('I request the detail of concert with id "{concert_id}" using AJAX')
def step_impl(context, concert_id):
    url = reverse("concerts:concert-detail", kwargs={"pk": concert_id})
    context.response = context.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")


@when("I request the detail of the existing concert using AJAX")
def step_impl(context):
    url = reverse("concerts:concert-detail", kwargs={"pk": context.concert_id})
    context.response = context.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")


@when("I submit the concert creation form using AJAX")
def step_impl(context):
    url = reverse("concerts:concert-create")
    artist = create_test_artist()
    venue = create_test_venue()
    context.response = context.client.post(
        url, {"artist": artist.id, "date": "2023-12-01", "venue": venue.id}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )


@then("I should receive a JSON response containing the correct concert details")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected status code 200, but got {context.response.status_code}"

    try:
        response_json = json.loads(context.response.content)
    except json.JSONDecodeError:
        raise AssertionError("Failed to decode the response content as JSON")

    assert "concert_id" in response_json, "The response JSON does not contain 'concert_id'"

    assert (
        response_json["concert_id"] == context.concert_id
    ), f"Expected concert_id {context.concert_id}, but got {response_json['concert_id']}"
