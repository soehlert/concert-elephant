from django.shortcuts import render, reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import ConcertForm
from .models import Artist, Concert, Venue


def home_page(request):
    return render(request, "pages/home.html")


class ArtistListView(ListView):
    model = Artist
    template_name = "concerts/artist_list.html"


class ArtistDetailView(DetailView):
    model = Artist


class ArtistCreateView(CreateView):
    model = Artist
    template_name = "concerts/artist_create.html"
    fields = [
        "name",
    ]

    def get_success_url(self):
        return reverse("concerts:artist-list")


class VenueListView(ListView):
    model = Venue
    template_name = "concerts/venue_list.html"


class VenueDetailView(DetailView):
    model = Venue


class VenueCreateView(CreateView):
    model = Venue
    template_name = "concerts/venue_create.html"
    fields = ["name", "city", "country"]

    def get_success_url(self):
        return reverse("concerts:venue-list")


class ConcertListView(ListView):
    model = Concert
    template_name = "concerts/concert_list.html"


class ConcertDetailView(DetailView):
    model = Concert


class ConcertCreateView(CreateView):
    model = Concert
    template_name = "concerts/concert_create.html"
    form_class = ConcertForm

    def get_success_url(self):
        return reverse("concerts:concert-list")
