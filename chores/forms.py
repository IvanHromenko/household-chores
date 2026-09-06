from django import forms
from .models import Chore


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ['title', 'notes', 'kind', 'freq_kind', 'freq_interval', 'freq_weekdays', 'due_date', 'claimed_by']
