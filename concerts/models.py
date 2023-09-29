from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django_countries.fields import CountryField


# Create your models here.
class Artist(models.Model):
    """The artist you saw"""

    name = models.CharField(max_length=100)

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
    """The venue you saw the concert"""

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = CountryField(default="US")

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
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="concerts")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="concerts")
    date = models.DateField()
    opener = models.CharField(max_length=100, null=True, blank=True)
    festival = models.BooleanField(default=False)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="concerts")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(f"{self.artist} - {self.venue} on {self.date}")

    @classmethod
    def attend_concert(cls, current_user, concert):
        concert.attendees.add(current_user)
