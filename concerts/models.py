from django.db import models
from django_countries.fields import CountryField


# Create your models here.
class Artist(models.Model):
    """The artist you saw"""

    name = models.CharField(max_length=100)

    def __str__(self):
        return str(f"{self.name}")


class Venue(models.Model):
    """The venue you saw the concert"""

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = CountryField()

    def __str__(self):
        if self.country:
            return str(f"{self.name} - {self.city}, {self.country}")
        else:
            return str(f"{self.name} - {self.city}")


class Concert(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="artist")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    date = models.DateField()
    opener = models.CharField(max_length=100, null=True, blank=True)
    festival = models.BooleanField(default=False)

    def __str__(self):
        return str(f"{self.artist} - {self.venue} on {self.date}")
