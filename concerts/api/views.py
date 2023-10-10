from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated

from ..models import Artist, Concert, ConcertReview, Venue
from .serializers import ArtistSerializer, ConcertReviewSerializer, ConcertSerializer, VenueSerializer


class ArtistViewset(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

    def get_permissions(self):
        print(self.request.headers)
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action == "list":
            return [permissions.AllowAny()]
        return super().get_permissions()


class VenueViewset(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_permissions(self):
        print(self.request.headers)
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action == "list":
            return [permissions.AllowAny()]
        return super().get_permissions()


class ConcertViewset(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer

    def get_permissions(self):
        print(self.request.headers)
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action == "list":
            return [permissions.AllowAny()]
        return super().get_permissions()


class ConcertReviewViewset(viewsets.ModelViewSet):
    queryset = ConcertReview.objects.all()
    serializer_class = ConcertReviewSerializer
    permission_classes = [IsAuthenticated]

    # Only let the author see their own reviews, nobody else
    # This does mean you'll get a 404 instead of a 403 when trying to
    # update/delete someone else's review by ID - privacy
    def get_queryset(self):
        return ConcertReview.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        review = self.get_object()
        if self.request.user != review.user:
            raise PermissionDenied("You can't edit this review!")
        serializer.save()

    def perform_destroy(self, instance):
        review = self.get_object()
        if self.request.user != review.user:
            raise PermissionDenied("You can't delete this review!")
        instance.delete()
