from bootstrap_datepicker_plus.widgets import DatePickerInput
from dal import autocomplete
from django import forms

from .models import Artist, Concert, Venue


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener", "festival"]
        widgets = {
            "date": DatePickerInput(options={"format": "MM/DD/YYYY"}),
            "artist": autocomplete.ModelSelect2(
                url="concerts:artist-autocomplete",
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Search...",
                    # Only trigger autocompletion after 2 characters have been typed
                    "data-minimum-input-length": 2,
                },
            ),
            "venue": autocomplete.ModelSelect2(
                url="concerts:venue-autocomplete",
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Search...",
                    # Only trigger autocompletion after 2 characters have been typed
                    "data-minimum-input-length": 2,
                },
            ),
        }


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            "name",
        ]

    def clean_name(self):
        """change `whatever_field` to the variable name of
        the field from the model
        """
        data = self.cleaned_data["name"].title()
        return data.title()


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ["name", "city", "country"]

    def clean_name(self):
        """change `whatever_field` to the variable name of
        the field from the model
        """
        data = self.cleaned_data["name"].title()
        return data.title()
