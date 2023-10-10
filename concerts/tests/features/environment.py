import logging

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

logging.basicConfig(level=logging.INFO)


def before_all(context):
    context.client = APIClient()
    User = get_user_model()
    if not User.objects.filter(username="testuser").exists():
        context.user = User.objects.create_user(username="testuser", password="testpassword")
    else:
        context.user = User.objects.get(username="testuser")

    context.last_artist_id = None
    context.last_venue_id = None


def after_all(context):
    call_command("flush", interactive=False, verbosity=0)  # This resets the database state
