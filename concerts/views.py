from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from .forms import ArtistForm, ConcertForm, VenueForm
from .models import Artist, Concert, Venue


def home_page(request):
    recent_artists = Artist.objects.all().order_by("-id")[:5]
    recent_concerts = Concert.objects.all().order_by("-date")[:5]
    recent_venues = Venue.objects.all().order_by("-id")[:5]
    popular_concerts = Concert.objects.all().annotate(num_attendees=Count("attendees")).order_by("-num_attendees")[:5]

    context = {
        "recent_artists": recent_artists,
        "recent_concerts": recent_concerts,
        "recent_venues": recent_venues,
        "popular_concerts": popular_concerts,
    }
    return render(request, "pages/home.html", context)


def main_search(request):
    q = request.POST.get("search_query")

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


class ArtistAutocomplete(View):
    def get_queryset(self, term):
        return Artist.objects.filter(name__icontains=term)

    def render_to_response(self, context):
        artists = self.get_queryset(context["term"])
        artist_data = [{"id": artist.id, "label": artist.name} for artist in artists]
        return JsonResponse(artist_data, safe=False)

    def get(self, request, *args, **kwargs):
        term = request.GET.get("term", "")
        context = {"term": term}
        return self.render_to_response(context)


class VenueAutocomplete(View):
    def get_queryset(self, term):
        # Filter venues that contain the search term in their name
        return Venue.objects.filter(name__icontains=term)

    def get(self, request, *args, **kwargs):
        term = request.GET.get("term", "")
        venues = self.get_queryset(term)

        # Prepare the data for autocomplete
        data = [{"id": venue.id, "label": str(venue)} for venue in venues]

        return JsonResponse(data, safe=False)


@login_required
def attend_concert(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    Concert.attend_concert(request.user, concert)

    return redirect("concerts:concert-list")


class ArtistListView(ListView):
    model = Artist
    template_name = "concerts/artist_list.html"
    paginate_by = 20

    def get_queryset(self):
        return Artist.objects.all().order_by("-id")


class ArtistDetailView(DetailView):
    model = Artist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_concerts"] = Concert.objects.filter(artist=self.object.id)
        return context


class ArtistCreateView(CreateView):
    model = Artist
    template_name = "concerts/artist_create.html"
    form_class = ArtistForm

    def get_success_url(self):
        return reverse("concerts:artist-list")

    def form_valid(self, form):
        artist_instance = form.save()

        # Check if the request is AJAX
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = {
                "status": "success",
                "artist": artist_instance.name,
                "artistId": artist_instance.id,
                "message": "Artist created successfully",
            }
            return JsonResponse(data)

        # For non-AJAX requests:
        messages.success(self.request, "Artist created successfully.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # Check if the request is AJAX
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # For non-AJAX requests:
        messages.error(self.request, "There was an error creating the artist.")
        return super().form_invalid(form)


class VenueListView(ListView):
    model = Venue
    template_name = "concerts/venue_list.html"
    paginate_by = 20


class VenueDetailView(DetailView):
    model = Venue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_concerts"] = Concert.objects.filter(venue=self.object.id)
        return context


class VenueCreateView(CreateView):
    model = Venue
    template_name = "concerts/venue_create.html"
    form_class = VenueForm

    def get_success_url(self):
        return reverse("concerts:venue-list")

    def form_valid(self, form):
        # Save the venue
        venue = form.save()

        # Check if the request is AJAX
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Venue successfully created!",
                    "venue": {"id": venue.id, "name": venue.name, "city": venue.city, "country": venue.country.code},
                }
            )

        # For non-AJAX requests:
        messages.success(self.request, "Venue successfully created.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # Prepare the error messages
        errors = {field: error[0] for field, error in form.errors.items()}

        # Check if the request is AJAX
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # For non-AJAX requests:
        messages.error(self.request, "There was an error creating the venue.")
        return self.render_to_response(self.get_context_data(form=form))


class ConcertListView(ListView):
    model = Concert
    template_name = "concerts/concert_list.html"
    paginate_by = 20


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["artist_form"] = ArtistForm()
        context["venue_form"] = VenueForm()
        return context

    def post(self, request, *args, **kwargs):
        print("POST request received for ConcertCreateView")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Get the artist name from the form data
        artist_name = form.cleaned_data.get("artist")

        # Find or create the artist instance by name
        artist, created = Artist.objects.get_or_create(name=artist_name)

        # Set the artist instance on the form's instance
        form.instance.artist = artist

        messages.success(self.request, "Concert successfully created!")

        # Continue with the regular form save
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        messages.error(self.request, "There was an error creating the concert.")
        return super().form_invalid(form)
