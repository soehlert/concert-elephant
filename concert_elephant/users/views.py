import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from concerts.forms import ConcertReviewForm
from concerts.models import ConcertReview

User = get_user_model()
logger = logging.getLogger(__name__)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    paginate_by = 10

    def get_sorted_concerts(self, user):
        logger.warning(f"Unrecognized sort option received: {self.request.GET.get('sort_by')}")
        sort_by = self.request.GET.get("sort_by", "-date")
        sort_options = ["artist", "-artist", "venue", "-venue", "date", "-date"]

        if sort_by not in sort_options:
            sort_by = "-date"

        secondary_sort = "date"

        if sort_by in ["artist", "-artist"]:
            concerts = user.concerts.annotate(lower_artist=Lower("artist__name")).order_by(
                sort_by.replace("artist", "lower_artist"), secondary_sort
            )
        elif sort_by in ["venue", "-venue"]:
            concerts = user.concerts.annotate(lower_venue=Lower("venue__name")).order_by(
                sort_by.replace("venue", "lower_venue"), secondary_sort
            )
        else:
            concerts = user.concerts.order_by(sort_by)

        return concerts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        search_query = self.request.GET.get("q")
        if search_query:
            concert_list = [
                concert
                for concert in user.concerts.filter(
                    Q(artist__name__icontains=search_query)
                    | Q(venue__name__icontains=search_query)
                    | Q(venue__city__icontains=search_query)
                    | Q(opener__name__icontains=search_query)
                )
            ]
        else:
            concert_list = [concert for concert in self.get_sorted_concerts(user)]

        for concert in concert_list:
            concert.user_review = ConcertReview.objects.filter(user=user, concert=concert).first()

        # Include the IDs of concerts the user is attending.
        user_concerts = user.concerts.values_list("id", flat=True)

        paginator = Paginator(concert_list, self.paginate_by)
        page = self.request.GET.get("page")
        concerts_with_reviews = paginator.get_page(page)

        context["in_user_detail"] = True
        context["concerts_with_reviews"] = concerts_with_reviews
        context["user_concerts"] = user_concerts
        context["review_form"] = ConcertReviewForm()
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
