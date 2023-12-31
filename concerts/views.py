import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q
from django.db.models.functions import Lower
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from .forms import ArtistForm, ConcertForm, ConcertReviewForm, VenueForm
from .models import Artist, Concert, ConcertReview, Venue

logger = logging.getLogger(__name__)


def home_page(request):
    recent_artists = Artist.objects.annotate(total_concerts=Count("concerts") + Count("opener_concerts")).order_by(
        "-created_at"
    )[:10]
    recent_concerts = Concert.objects.select_related("artist", "venue").order_by("-date")[:10]
    recent_venues = Venue.objects.all().order_by("-created_at")[:10]
    popular_artists = Artist.objects.annotate(total_concerts=Count("concerts") + Count("opener_concerts")).order_by(
        "-total_concerts"
    )[:10]
    popular_concerts = Concert.objects.all().annotate(num_attendees=Count("attendees")).order_by("-num_attendees")[:10]
    popular_venues = Venue.objects.annotate(num_shows=Count("concerts")).order_by("-num_shows")[:10]

    context = {
        "recent_artists": recent_artists,
        "recent_concerts": recent_concerts,
        "recent_venues": recent_venues,
        "popular_artists": popular_artists,
        "popular_concerts": popular_concerts,
        "popular_venues": popular_venues,
    }
    return render(request, "home.html", context)


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


class UnifiedAutocomplete(View):
    def get_queryset(self, model_class, term, search_field="name"):
        kwargs = {f"{search_field}__icontains": term}
        return model_class.objects.filter(**kwargs)

    def get(self, request, model_name, *args, **kwargs):
        term = request.GET.get("term", "")
        search_field = "name"

        # Map model name to actual model class
        models_map = {
            "artist": Artist,
            "venue": Venue,
            "opener": Artist,
        }

        model_class = models_map.get(model_name)

        items = self.get_queryset(model_class, term, search_field)
        data = [{"id": item.id, "label": str(item)} for item in items]

        return JsonResponse(data, safe=False)


@login_required
def attend_concert(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    Concert.attend_concert(request.user, concert)
    return handle_redirection(request, concert)


@login_required
def unattend_concert(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    concert.attendees.remove(request.user)

    messages.info(
        request,
        "Concert removed from your profile. If you had a review, your review "
        "has been saved and can be accessed if you re-add the concert.",
    )

    return handle_redirection(request, concert)


def handle_redirection(request, concert):
    next_page = request.POST.get("next", "") or request.GET.get("next", "")

    if next_page == "concert-list":
        return redirect("concerts:concert-list")
    elif next_page == "artist-detail":
        return redirect("concerts:artist-detail", pk=concert.artist.pk)
    elif next_page == "user-detail":
        return redirect("users:detail", request.user.username)
    else:
        return redirect("concerts:concert-list")


class ArtistListView(ListView):
    model = Artist
    template_name = "concerts/artist_list.html"
    paginate_by = 20

    def get_queryset(self):
        sort_options = ["name", "-name", "-created_at", "concert_count", "-concert_count"]
        sort_by = self.request.GET.get("sort_by", "-created_at")
        if sort_by not in sort_options:
            logger.warning(f"Unrecognized sort option received: {self.request.GET.get('sort_by')}")
            sort_by = "-created_at"

        queryset = (
            Artist.objects.annotate(
                main_concert_count=Count("concerts"), opener_concert_count=Count("opener_concerts")
            )
            .annotate(concert_count=F("main_concert_count") + F("opener_concert_count"))
            .order_by(sort_by)
        )

        return queryset


class ArtistDetailView(DetailView):
    model = Artist
    template_name = "concerts/artist_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get concerts where the artist is the main performer
        main_concerts = Concert.objects.filter(artist=self.object.id).select_related("venue")

        # Get concerts where the artist is an opener
        opener_concerts = Concert.objects.filter(opener=self.object.id).select_related("venue")

        # Combine the querysets
        total_concerts = main_concerts | opener_concerts
        total_concerts_count = total_concerts.count()

        context["recent_concerts"] = total_concerts
        context["total_concerts_count"] = total_concerts_count

        # Add the user_concerts to the context
        if self.request.user.is_authenticated:
            context["user_concerts"] = Concert.objects.filter(attendees=self.request.user).values_list("id", flat=True)
        else:
            context["user_concerts"] = []

        # Indicate that we're on the artist detail page
        # used for redirection when unattending/attending a concert
        context["in_artist_detail"] = True

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            artist = context.get("object")
            if artist:
                return JsonResponse({"name": artist.name})
            else:
                return JsonResponse({"error": "Artist not found"}, status=404)
        else:
            return render(self.request, self.template_name, context)


class ArtistCreateView(LoginRequiredMixin, CreateView):
    model = Artist
    template_name = "concerts/artist_create.html"
    form_class = ArtistForm

    def get_success_url(self):
        return reverse("concerts:artist-list")

    def form_valid(self, form):
        artist_instance = form.save()

        # Check if the request is AJAX
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
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
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
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
        sort_options = [
            "name",
            "-name",
            "city",
            "-city",
            "state",
            "-state",
            "country",
            "-country",
            "concert_count",
            "-concert_count",
            "-created_at",
        ]
        sort_by = self.request.GET.get("sort_by", "-created_at")
        if sort_by not in sort_options:
            logger.warning(f"Unrecognized sort option received: {self.request.GET.get('sort_by')}")
            sort_by = "-created_at"

        queryset = Venue.objects.annotate(concert_count=Count("concerts")).order_by(sort_by)

        return queryset


class VenueDetailView(DetailView):
    model = Venue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_concerts"] = Concert.objects.filter(venue=self.object.id).select_related("artist")
        return context


class VenueCreateView(LoginRequiredMixin, CreateView):
    model = Venue
    template_name = "concerts/venue_create.html"
    form_class = VenueForm

    def get_success_url(self):
        return reverse("concerts:venue-list")

    def form_valid(self, form):
        venue = form.save()

        # Check if the request is AJAX
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Venue successfully created!",
                    "venue": {
                        "id": venue.id,
                        "name": venue.name,
                        "city": venue.city,
                        "state": venue.state,
                        "country": venue.country.code,
                    },
                }
            )

        # For non-AJAX requests:
        messages.success(self.request, "Venue successfully created.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        errors = {field: error[0] for field, error in form.errors.items()}

        # Check if the request is AJAX
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # For non-AJAX requests:
        messages.error(self.request, "There was an error creating the venue.")
        return super().form_invalid(form)


class ConcertListView(ListView):
    model = Concert
    template_name = "concerts/concert_list.html"
    paginate_by = 20

    def get_queryset(self):
        sort_options = ["artist", "-artist", "venue", "-venue", "date", "-date"]
        sort_by = self.request.GET.get("sort_by", "-date")

        if sort_by not in sort_options:
            logger.warning(f"Unrecognized sort option received: {self.request.GET.get('sort_by')}")
            sort_by = "-date"

        if sort_by == "artist" or sort_by == "-artist":
            queryset = Concert.objects.annotate(lower_artist=Lower("artist__name")).order_by(
                sort_by.replace("artist", "lower_artist")
            )
        elif sort_by == "venue" or sort_by == "-venue":
            queryset = Concert.objects.annotate(lower_venue=Lower("venue__name")).order_by(
                sort_by.replace("venue", "lower_venue")
            )
        else:
            queryset = Concert.objects.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the user_concerts to the context
        if self.request.user.is_authenticated:
            context["user_concerts"] = Concert.objects.filter(attendees=self.request.user).values_list("id", flat=True)
        else:
            context["user_concerts"] = []

        # Indicate that we're on the concert list view
        # used for redirection when unattending/attending a concert
        context["in_concert_list"] = True

        return context


class ConcertDetailView(DetailView):
    model = Concert
    context_object_name = "concert"
    template_name = "concerts/concert_detail.html"

    def get_object(self, **kwargs):
        # Use select_related to fetch related artist and venue in a single query
        return get_object_or_404(Concert.objects.select_related("artist", "venue"), pk=self.kwargs["pk"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_concerts"] = Concert.objects.filter(attendees=self.request.user).values_list("id", flat=True)
        else:
            context["user_concerts"] = []

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            "AJAX request received for ConcertDetailView."
            concert = context.get("concert")
            data = {
                "concert_id": concert.pk,
                "artist": concert.artist.name,
                "date": concert.date.strftime("%Y-%m-%d"),
            }
            return JsonResponse(data)

        return super().render_to_response(context, **response_kwargs)


class ConcertCreateView(LoginRequiredMixin, CreateView):
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
        artist_name = form.cleaned_data.get("artist")

        try:
            artist_instance = Artist.objects.get(name=artist_name)
        except Artist.DoesNotExist:
            artist_form = ArtistForm(data={"name": artist_name})
            if artist_form.is_valid():
                artist_instance = artist_form.save(commit=True)
            else:
                # Combining errors from the main form and the artist form
                form._errors = {**form._errors, **artist_form.errors}
                return self.form_invalid(form)

        # Assign the artist to the concert instance
        form.instance.artist = artist_instance

        # Save the form instance but don't commit to DB yet
        concert = form.save(commit=False)
        concert.save()  # This saves the instance to the database, allowing many-to-many operations

        for opener in form.cleaned_data["opener"]:
            concert.opener.add(opener)

        # Automatically set the creator as an attendee
        concert.attendees.add(self.request.user)

        messages.success(self.request, "Concert successfully created!")

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success"})

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)

        non_field_errors = form.non_field_errors()
        if non_field_errors:
            messages.error(self.request, non_field_errors)
        return super().form_invalid(form)


class ConcertReviewCreateView(LoginRequiredMixin, CreateView):
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
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # For non-AJAX requests:
        messages.error(self.request, "There was an error creating the review.")
        return super().form_invalid(form)


class ConcertReviewDetailView(LoginRequiredMixin, View):
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


class ConcertReviewUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(ConcertReview, id=review_id)

        # Check if the current user is the author of the review
        if review.user != self.request.user:
            return HttpResponseForbidden("You don't have permission to edit this review.")

        note = request.POST.get("note")
        rating = request.POST.get("rating")

        review.note = note
        review.rating = rating

        try:
            review.full_clean()  # This will run all model field validations
            review.save()
        except ValidationError as e:
            return JsonResponse({"success": False, "errors": e.message_dict}, status=400)

        return JsonResponse({"success": True, "note": review.note, "rating": review.rating, "reviewId": review_id})


class ConcertReviewDeleteView(LoginRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        review_id = kwargs.get("review_id")
        review = get_object_or_404(ConcertReview, id=review_id)

        # Check if the current user is the author of the review
        if review.user != self.request.user:
            return HttpResponseForbidden("You don't have permission to edit this review.")

        try:
            review = ConcertReview.objects.get(pk=review_id)
            review.delete()
            return JsonResponse({"success": True, "message": "Review deleted successfully."})
        except ConcertReview.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Review not found."}, status=404)
