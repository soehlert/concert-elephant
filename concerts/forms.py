from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django_countries.widgets import CountrySelectWidget

from .models import Artist, Concert, Venue


class ConcertForm(forms.ModelForm):
    # artist = forms.ModelChoiceField(
    #     queryset=Artist.objects.all(),
    #     widget=forms.Select(attrs={"class": "form-control", "id": "artist-autocomplete"}),
    # )

    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener", "festival"]
        widgets = {
            "date": DatePickerInput(options={"format": "MM/DD/YYYY"}, attrs={"class": "form-control"}),
        }

    #
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["artist"].queryset = Artist.objects.all()


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
