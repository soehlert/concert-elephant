from django.urls import path

from . import views

app_name = "route_manager"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("artists/", views.ArtistListView.as_view(), name="artist-list"),
    path("artists/add", views.ArtistCreateView.as_view(), name="artist-create"),
    path("artists/<int:pk>", views.ArtistDetailView.as_view(), name="artist-detail"),
    path("venues/", views.VenueListView.as_view(), name="venue-list"),
    path("venues/add", views.VenueCreateView.as_view(), name="venue-create"),
    path("venues/<int:pk>", views.VenueDetailView.as_view(), name="artist-detail"),
    path("concerts/", views.ConcertListView.as_view(), name="concert-list"),
    path("concerts/add", views.ConcertCreateView.as_view(), name="concert-create"),
    path("concerts/<int:pk>", views.ConcertDetailView.as_view(), name="concert-detail"),
]
