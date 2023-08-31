from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render, reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import ArtistForm, ConcertForm, VenueForm
from .models import Artist, Concert, Venue


def home_page(request):
    return render(request, "pages/home.html")


def main_search(request):
    q = request.GET["search_query"]

    artists = Artist.objects.filter(name__icontains=q)
    concerts = Concert.objects.filter(
        Q(artist__name__icontains=q) | Q(venue__name__icontains=q) | Q(venue__city__icontains=q)
    )
    venues = Venue.objects.filter(Q(name__icontains=q) | Q(city__icontains=q))
    return render(
        request,
        "main_search.html",
        {"artists": artists, "concerts": concerts, "venues": venues, "page_name": "Search Results", "q": q},
    )


class ArtistAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Artist.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class VenueAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Venue.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


@login_required
def attend_concert(request, pk):
    concert = Concert.objects.get(pk=pk)
    Concert.attend_concert(request.user, concert)

    return redirect("concerts:concert-list")


class ArtistListView(ListView):
    model = Artist
    template_name = "concerts/artist_list.html"


class ArtistDetailView(DetailView):
    model = Artist


class ArtistCreateView(CreateView):
    model = Artist
    template_name = "concerts/artist_create.html"
    form_class = ArtistForm

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
    form_class = VenueForm

    def get_success_url(self):
        return reverse("concerts:venue-list")


class ConcertListView(ListView):
    model = Concert
    template_name = "concerts/concert_list.html"


class ConcertDetailView(DetailView):
    model = Concert

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_concerts"] = Concert.objects.filter(attendees=self.request.user).values_list("id", flat=True)
        return context


class ConcertCreateView(CreateView):
    model = Concert
    template_name = "concerts/concert_create.html"
    form_class = ConcertForm

    def get_success_url(self):
        return reverse("concerts:concert-list")
