from django import forms
from django.shortcuts import get_object_or_404
# from .models import *


class SearchField(forms.Form):
    keyword = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter name or accession number here'}), max_length=250)
    accession_number_only = forms.BooleanField(label="Accession Number", required=False)

    def clean(self):
        cleaned_data = super().clean()
        self.keyword = cleaned_data.get("keyword")
        self.accession_number_only = cleaned_data.get("accession_number_only")
        #self.aggregate_results = cleaned_data.get("aggregate_results")