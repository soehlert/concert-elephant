from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django_countries.widgets import CountrySelectWidget

from .models import Artist, Concert, Venue


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener"]
        widgets = {
            "date": DatePickerInput(options={"format": "MM/DD/YYYY"}, attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        opener_fields = {key: forms.CharField(required=False) for key in self.data if key.startswith("opener-")}
        self.fields.update(opener_fields)

    def clean(self):
        cleaned_data = super().clean()
        opener_artists = []

        # Create a list of keys to check before modifying cleaned_data
        opener_keys = [key for key in cleaned_data if key.startswith("opener-")]

        for key in opener_keys:
            value = cleaned_data.get(key)
            print(f"{key} = {value}")
            if value:
                try:
                    artist = Artist.objects.get(id=value)
                    opener_artists.append(artist)
                except Artist.DoesNotExist:
                    self.add_error(key, f"Artist named {value} does not exist.")

        cleaned_data["opener"] = opener_artists
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()  # Save the Concert instance first to get an ID.

            # Associate the artists with the opener.
            for artist in self.cleaned_data["opener"]:
                instance.opener.add(artist)

        return instance


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
