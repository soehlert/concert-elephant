from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from .forms import ArtistForm, ConcertForm, ConcertReviewForm, VenueForm
from .models import Artist, Concert, ConcertReview, Venue


def home_page(request):
    recent_artists = Artist.objects.all().order_by("-id")[:5]
    recent_concerts = Concert.objects.select_related("artist", "venue").order_by("-date")[:5]
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
        return Venue.objects.filter(name__icontains=term)

    def get(self, request, *args, **kwargs):
        term = request.GET.get("term", "")
        venues = self.get_queryset(term)

        # Prepare the data for autocomplete
        data = [{"id": venue.id, "label": str(venue)} for venue in venues]

        return JsonResponse(data, safe=False)


class OpenerAutocomplete(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("term", "")
        artists = Artist.objects.filter(name__icontains=query)[:10]
        results = [{"id": artist.id, "label": artist.name, "value": artist.name} for artist in artists]
        return JsonResponse(results, safe=False)


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
        context["recent_concerts"] = Concert.objects.filter(artist=self.object.id).select_related("venue")
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

    def get_queryset(self):
        return Venue.objects.all().order_by("-id")


class VenueDetailView(DetailView):
    model = Venue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_concerts"] = Concert.objects.filter(venue=self.object.id).select_related("artist")
        return context


class VenueCreateView(CreateView):
    model = Venue
    template_name = "concerts/venue_create.html"
    form_class = VenueForm

    def get_success_url(self):
        return reverse("concerts:venue-list")

    def form_valid(self, form):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.GET.get("sort_by", "date")  # Default to sorting by date
        order = self.request.GET.get("order", "asc")  # Default to ascending order
        prefix = "-" if order == "desc" else ""
        return queryset.order_by(f"{prefix}{sort_by}")

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            page_data = context.get("page_obj").object_list

            data = []
            for concert in page_data:
                concert_data = {
                    "pk": concert.pk,
                    "fields": {
                        "artist": str(concert.artist),
                        "venue": str(concert.venue),
                        "date": concert.date.strftime("%Y-%m-%d"),
                        "openers": [str(opener) for opener in concert.opener.all()],
                    },
                }
                data.append(concert_data)

            return JsonResponse({"concerts": data})
        return super().render_to_response(context, **response_kwargs)


class ConcertDetailView(DetailView):
    model = Concert
    context_object_name = "concert"

    def get_object(self, **kwargs):
        # Use select_related to fetch related artist and venue in a single query
        return get_object_or_404(Concert.objects.select_related("artist", "venue"), pk=self.kwargs["pk"])

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

    def form_valid(self, form):
        # Extract the artist name from the form data
        artist_name = form.cleaned_data.get("artist")

        try:
            artist_instance = Artist.objects.get(name=artist_name)
        except Artist.DoesNotExist:
            artist_form = ArtistForm(data={"name": artist_name})
            if artist_form.is_valid():
                artist_instance = artist_form.save(commit=True)
            else:
                form._errors = {**form._errors, **artist_form.errors}
                return self.form_invalid(form)

        # Assign the artist to the concert instance
        form.instance.artist = artist_instance

        # Save the form instance but don't commit to DB yet
        concert = form.save(commit=False)
        concert.save()  # This will save the instance to DB, allowing many-to-many operations

        # Automatically set the creator as an attendee
        concert.attendees.add(self.request.user)

        messages.success(self.request, "Concert successfully created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        messages.error(self.request, "There was an error creating the concert.")
        return super().form_invalid(form)


class ConcertReviewCreateView(CreateView):
    model = ConcertReview
    form_class = ConcertReviewForm
    template_name = "users/user_detail.html"

    def get_success_url(self):
        return reverse_lazy("users:detail", args=[self.request.user.username])

    def form_valid(self, form):
        concert = get_object_or_404(Concert, pk=self.kwargs["pk"])

        # Ensure the user hasn't reviewed this concert already
        if ConcertReview.objects.filter(user=self.request.user, concert=concert).exists():
            form.add_error(None, "You've already reviewed this concert!")
            return self.form_invalid(form)

        review = form.save(commit=False)
        review.user = self.request.user
        review.concert = concert
        review.save()

        # Check if it's an AJAX request
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            data = {"success": True}
            return JsonResponse(data)

        # For non-AJAX requests:
        messages.success(self.request, "Venue successfully created.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        errors = {field: error[0] for field, error in form.errors.items()}

        # Check if the request is AJAX
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # For non-AJAX requests:
        messages.error(self.request, "There was an error creating the review.")
        return self.render_to_response(self.get_context_data(form=form))


class ConcertReviewDetailView(View):
    def get(self, request, *args, **kwargs):
        review_id = kwargs.get("review_id")
        try:
            review = ConcertReview.objects.get(pk=review_id)
            review_data = {
                "note": review.note,
                "rating": review.rating,
                "review_id": review_id,
            }
            return JsonResponse(review_data)
        except ConcertReview.DoesNotExist:
            return JsonResponse({"error": "Review not found"}, status=404)


class ConcertReviewUpdateView(View):
    def post(self, request, *args, **kwargs):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(ConcertReview, id=review_id)

        note = request.POST.get("note")
        rating = request.POST.get("rating")

        review.note = note
        review.rating = rating
        review.save()

        try:
            # Attempt to save. This may fail due to model field validations.
            review.full_clean()  # This will run all model field validations
            review.save()
        except ValidationError as e:
            # Catch validation errors and return them
            return JsonResponse({"success": False, "errors": e.message_dict}, status=400)

        return JsonResponse({"success": True, "note": review.note, "rating": review.rating, "reviewId": review_id})


class ConcertReviewDeleteView(View):
    def delete(self, request, *args, **kwargs):
        review_id = kwargs.get("review_id")
        try:
            review = ConcertReview.objects.get(pk=review_id)
            review.delete()
            return JsonResponse({"success": True, "message": "Review deleted successfully."})
        except ConcertReview.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Review not found."}, status=404)
