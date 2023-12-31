from django.urls import path

from . import views
from .views import UnifiedAutocomplete

app_name = "concerts"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("search/", views.main_search, name="main_search"),
    path("autocomplete/<str:model_name>/", UnifiedAutocomplete.as_view(), name="unified-autocomplete"),
    # Artists
    path("artists/", views.ArtistListView.as_view(), name="artist-list"),
    path("artists/add/", views.ArtistCreateView.as_view(), name="artist-create"),
    path("artists/<int:pk>/", views.ArtistDetailView.as_view(), name="artist-detail"),
    # Venues
    path("venues/", views.VenueListView.as_view(), name="venue-list"),
    path("venues/add/", views.VenueCreateView.as_view(), name="venue-create"),
    path("venues/<int:pk>", views.VenueDetailView.as_view(), name="venue-detail"),
    # Concerts
    path("concerts/", views.ConcertListView.as_view(), name="concert-list"),
    path("concerts/add/", views.ConcertCreateView.as_view(), name="concert-create"),
    path("concerts/<int:pk>/", views.ConcertDetailView.as_view(), name="concert-detail"),
    path("concerts/attend/<int:pk>/", view=views.attend_concert, name="attend-concert"),
    path("concerts/unattend/<int:pk>/", views.unattend_concert, name="unattend-concert"),
    # Concert Reviews
    path("concert/<int:pk>/add_review/", views.ConcertReviewCreateView.as_view(), name="add-concert-review"),
    path("concert/review/<int:review_id>/", views.ConcertReviewDetailView.as_view(), name="get-concert-review"),
    path(
        "concert/review/update/<int:review_id>/", views.ConcertReviewUpdateView.as_view(), name="update-concert-review"
    ),
    path(
        "concert/review/delete/<int:review_id>/", views.ConcertReviewDeleteView.as_view(), name="delete-concert-review"
    ),
]
