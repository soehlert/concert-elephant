from django.urls import path

from . import views
from .views import ArtistAutocomplete, VenueAutocomplete

app_name = "concerts"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("search/", views.main_search, name="main_search"),
    # Artists
    path(
        "artist-autocomplete/",
        ArtistAutocomplete.as_view(create_field="name", validate_create=True),
        name="artist-autocomplete",
    ),
    path("artists/", views.ArtistListView.as_view(), name="artist-list"),
    path("artists/add/", views.ArtistCreateView.as_view(), name="artist-create"),
    path("artists/<int:pk>", views.ArtistDetailView.as_view(), name="artist-detail"),
    # Venues
    path("venue-autocomplete/", VenueAutocomplete.as_view(), name="venue-autocomplete"),
    path("venues/", views.VenueListView.as_view(), name="venue-list"),
    path("venues/add/", views.VenueCreateView.as_view(), name="venue-create"),
    path("venues/<int:pk>", views.VenueDetailView.as_view(), name="venue-detail"),
    # Concerts
    path("concerts/", views.ConcertListView.as_view(), name="concert-list"),
    path("concerts/add/", views.ConcertCreateView.as_view(), name="concert-create"),
    path("concerts/<int:pk>", views.ConcertDetailView.as_view(), name="concert-detail"),
    path("concerts/attend/<int:pk>", view=views.attend_concert, name="attend-concert"),
]
