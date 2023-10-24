from django.conf import settings


def debug_mode(request):
    return {"DEBUG_MODE": settings.DEBUG}
