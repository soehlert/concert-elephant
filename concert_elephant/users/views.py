from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from concerts.forms import ConcertReviewForm
from concerts.models import ConcertReview

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Attach the review to each concert if it exists
        concert_list = [concert for concert in user.concerts.all()]
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
