import logging

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

logging.basicConfig(level=logging.INFO)


def before_all(context):
    context.client = Client()
    User = get_user_model()
    if not User.objects.filter(username="testuser").exists():
        context.user = User.objects.create_user(username="testuser", password="testpassword")
    else:
        context.user = User.objects.get(username="testuser")
    context.protected_page_url = reverse("concerts:artist-create")


def after_all(context):
    context.user.delete()
