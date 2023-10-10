from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from django_countries.fields import CountryField


# Create your models here.
class Artist(models.Model):
    """The artist you saw"""

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # Don't allow multiple bands with the same name
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="artist_name_unique",
            ),
        ]

    def __str__(self):
        return str(f"{self.name}")

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Venue(models.Model):
    """The venue you saw the concert at"""

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = CountryField(default="US")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["name", "city"]

    def __str__(self):
        if self.country:
            return str(f"{self.name} - {self.city}, {self.country}")
        else:
            return str(f"{self.name} - {self.city}")

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.city = self.city.title()
        super().save(*args, **kwargs)


class Concert(models.Model):
    """The concert itself"""

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="concerts")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="concerts")
    date = models.DateField(default=timezone.now)
    opener = models.ManyToManyField(Artist, related_name="opener_concerts", blank=True)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="concerts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(f"{self.artist} - {self.venue} on {self.date}")

    @classmethod
    def attend_concert(cls, current_user, concert):
        concert.attendees.add(current_user)


class ConcertReview(models.Model):
    """Allows users to give ratings and save notes on their concerts"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Concert Reviews"

    def __str__(self):
        return str(f"{self.user} - {self.concert}")
