from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms

from .models import Concert


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = ["artist", "venue", "date", "opener", "festival"]
        widgets = {
            "date": DatePickerInput(options={"format": "MM/DD/YYYY"}),
        }
