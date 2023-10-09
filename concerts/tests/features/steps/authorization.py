from behave import given, then, when
from django.http import Http404
from django.urls import reverse


@given("I have valid credentials")
def step_impl(context):
    pass  # We've already created a user in before_all, so we don't need to recreate it here.


@given("I am an unauthenticated user")
def step_impl(context):
    context.client.logout()


@when("I try to access a protected page")
def step_impl(context):
    context.response = context.client.get(context.protected_page_url)


@when("I login and access a protected page")
def step_impl(context):
    context.client.login(username="testuser", password="testpassword")
    context.response = context.client.get(context.protected_page_url)


@then("I should be able to view the page")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200 status code, but got {context.response.status_code}"


@then("I get a {status_code:d} status code")
def step_impl(context, status_code):
    context.test.assertEqual(context.response.status_code, status_code)


@then('I am on the "{url}" page')
def step_impl(context, url):
    try:
        url = reverse(url)
        context.response = context.client.get(url)
        assert context.response.status_code == 200, f"Expected 200 status code, but got {context.response.status_code}"
    except Http404:
        assert False, f"Unable to resolve the URL pattern name {url}"
