from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms

from .models import Artist, Concert, Venue


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener", "festival"]
        widgets = {
            "date": DatePickerInput(options={"format": "MM/DD/YYYY"}),
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
