from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django_countries.widgets import CountrySelectWidget

from .models import Artist, Concert, Venue


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener", "festival"]
        widgets = {
            "date": DatePickerInput(options={"format": "MM/DD/YYYY"}, attrs={"class": "form-control"}),
        }


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            "name",
        ]


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ["name", "city", "country"]
        widgets = {"country": CountrySelectWidget(attrs={"class": "form-control"})}
