from django import forms
from .models import *


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["name", "link", "custom", "image", "start", "end", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.TextInput(attrs={"class": "form-control"}),
            "custom": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "start": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 60}),
            "end": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 60}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }



class FacebookGroupForm(forms.ModelForm):
    class Meta:
        model = FacebookGroup
        fields = '__all__'

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'