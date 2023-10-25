from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django_countries.widgets import CountrySelectWidget
from localflavor.us.forms import USStateField, USStateSelect

from .models import Artist, Concert, ConcertReview, Venue


class ConcertReviewForm(forms.ModelForm):
    class Meta:
        model = ConcertReview
        fields = ["rating", "note"]


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

        opener_keys = [key for key in cleaned_data if key.startswith("opener-")]

        for key in opener_keys:
            value = cleaned_data.get(key)
            if value:
                try:
                    artist = Artist.objects.get(id=value)
                    opener_artists.append(artist)
                except Artist.DoesNotExist:
                    self.add_error(key, f"Artist named {value} does not exist.")

        # Ensure uniqueness across main artist and openers
        main_artist = cleaned_data.get("artist")
        all_artists_set = {main_artist.id} if main_artist else set()

        for artist in opener_artists:
            if artist.id in all_artists_set:
                self.add_error(
                    None,
                    f"Artist {artist.name} is duplicated. Make sure the artist is not set as both main and opener or duplicated in openers.",  # noqa
                )
            all_artists_set.add(artist.id)

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
    state = USStateField(widget=USStateSelect(), required=False)

    class Meta:
        model = Venue
        fields = ["name", "city", "state", "country"]
        widgets = {"country": CountrySelectWidget(attrs={"class": "form-control"})}

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")

        if country != "US":
            cleaned_data["state"] = None

        return cleaned_data
