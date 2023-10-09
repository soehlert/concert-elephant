import json

from behave import given, then, when
from django.contrib.auth import get_user_model
from django.urls import reverse

from concerts.tests.features.steps.common import create_test_concert, create_test_review


@given('"{username}" has written a concert review')
def step_impl(context, username):
    user = get_user_model().objects.get(username=username)
    concert = create_test_concert("2023-01-01")
    review = create_test_review(user, concert, 5, "A test note")
    context.review = review
    context.review_id = review.id


@when('"{username}" tries to update {username2} concert review')
def step_impl(context, username, username2):
    user = get_user_model().objects.get(username=username)
    context.client.login(username=user.username, password="testpassword")
    context.response = context.client.post(
        reverse("concerts:update-concert-review", args=[context.review.id]),
        {"note": "Updated note", "rating": 4},
        follow=True,
    )


@when("{username} tries to delete {author}s concert review")
def step_impl(context, username, author):
    delete_url = reverse("concerts:delete-concert-review", args=[context.review_id])
    context.response = context.client.delete(delete_url)


@then("the delete operation should be successful")
def step_impl(context):
    assert context.response.status_code == 200
    response_data = json.loads(context.response.content.decode("utf-8"))
    assert response_data["success"] == True  # noqa: E712


@then("the delete operation should be forbidden")
def step_impl(context):
    assert context.response.status_code == 403


@then("the review update should be successful")
def step_impl(context):
    response_data = json.loads(context.response.content.decode("utf-8"))

    assert context.response.status_code == 200
    assert (
        response_data["success"] == True  # noqa: E712,E501
    ), f"Expected success to be True, but got {response_data['success']}"
    assert (
        response_data["note"] == "Updated note"
    ), f"Expected note to be 'Updated note', but got {response_data['note']}"
    assert response_data["rating"] == 4, f"Expected rating to be 4, but got {response_data['rating']}"
    assert (
        response_data["reviewId"] == context.review_id
    ), f"Expected reviewId to be {context.review_id}, but got {response_data['reviewId']}"


@then("the review update should be denied")
def step_impl(context):
    assert context.response.status_code == 403
