from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from concert_elephant.users.api.views import UserViewSet
from concerts.api.views import ArtistViewset, ConcertViewset, VenueViewset

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("artists", ArtistViewset)
router.register("concerts", ConcertViewset)
router.register("venues", VenueViewset)
router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls
