from rest_framework import serializers

from ..models import Artist, Concert, Venue


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["name"]


class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener", "festival"]


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ["name", "city", "country"]
