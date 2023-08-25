from rest_framework import viewsets

from ..models import Artist, Concert, Venue
from .serializers import ArtistSerializer, ConcertSerializer, VenueSerializer


class ArtistViewset(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


class VenueViewset(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


class ConcertViewset(viewsets.ModelViewSet):
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer
