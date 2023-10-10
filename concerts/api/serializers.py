from rest_framework import serializers

from ..models import Artist, Concert, ConcertReview, Venue


class ArtistSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:v1:artist-detail")
    total_as_artist = serializers.SerializerMethodField()
    total_as_opener = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ["id", "url", "name", "created_at", "total_as_artist", "total_as_opener"]

    def get_total_as_artist(self, obj):
        return obj.concerts.count()

    def get_total_as_opener(self, obj):
        return obj.opener_concerts.count()


class VenueSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:v1:venue-detail")
    total_concerts = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = ["id", "url", "name", "city", "country", "created_at", "total_concerts"]

    def get_total_concerts(self, obj):
        return obj.concerts.count()


class ConcertSerializer(serializers.ModelSerializer):
    artist = serializers.HyperlinkedRelatedField(view_name="api:v1:artist-detail", queryset=Artist.objects.all())
    artist_name = serializers.StringRelatedField(source="artist.name", read_only=True)
    venue = serializers.HyperlinkedRelatedField(view_name="api:v1:venue-detail", queryset=Venue.objects.all())
    venue_name = serializers.StringRelatedField(source="venue.name", read_only=True)
    total_attendees = serializers.SerializerMethodField()

    class Meta:
        model = Concert
        fields = [
            "id",
            "artist",
            "artist_name",
            "venue",
            "venue_name",
            "date",
            "created_at",
            "opener",
            "total_attendees",
        ]

    def get_total_attendees(self, obj):
        return obj.attendees.count()


class ConcertReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.StringRelatedField(source="user.username", read_only=True)
    concert = serializers.HyperlinkedRelatedField(view_name="api:v1:concert-detail", queryset=Concert.objects.all())

    class Meta:
        model = ConcertReview
        fields = ["id", "user", "user_name", "concert", "rating", "note", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        review = ConcertReview.objects.create(**validated_data)
        return review
