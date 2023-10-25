from behave import then, when
from django.http import Http404
from django.urls import reverse

from concerts.tests.features.steps.common import (
    create_test_artist,
    create_test_concert,
    create_test_review,
    create_test_venue,
)


@when("I try to access a protected page {url_name}")
def step_impl(context, url_name):
    concert = create_test_concert(artist=create_test_artist(), venue=create_test_venue(), date="2023-01-01")
    review = create_test_review(user=context.user, concert=concert, rating=5, note="A test note")

    # URLs mapped to the type of parameter they require
    param_mapping = {
        "concerts:concert-detail": [concert.id],
        "concerts:attend-concert": [concert.id],
        "concerts:unattend-concert": [concert.id],
        "concerts:add-concert-review": [concert.id],
        "concerts:update-concert-review": [review.id],
        "concerts:delete-concert-review": [review.id],
        "concerts:get-concert-review": [review.id],
    }

    if url_name in param_mapping:
        actual_url = reverse(url_name, args=param_mapping[url_name])
    else:
        actual_url = reverse(url_name)

    context.response = context.client.get(actual_url)
    context.tested_url_name = url_name


@then("I should be able to view the page")
def step_impl(context):
    if context.tested_url_name in ["concerts:attend-concert", "concerts:unattend-concert"]:
        expected_status = 302
        expected_location = reverse("concerts:concert-list")
        assert (
            context.response["Location"] == expected_location
        ), f"Unexpected redirect location: {context.response['Location']}"
    else:
        expected_status = 200

    assert (
        context.response.status_code == expected_status
    ), f"Expected {expected_status} status code, but got {context.response.status_code}"


@then('I am on the "{url}" page')
def step_impl(context, url):
    try:
        url = reverse(url)
        context.response = context.client.get(url)
        assert context.response.status_code == 200, f"Expected 200 status code, but got {context.response.status_code}"
    except Http404:
        assert False, f"Unable to resolve the URL pattern name {url}"
