from django import forms
from django.forms import ModelForm
from results.models import AccountData


class AccountDataForm(ModelForm):
    class Meta:
        model = AccountData
        # exclude = ['author', 'updated', 'created', ]
        fields = ['text']
        widgets = {
            'text': forms.TextInput(
                attrs={'id': 'post-text', 'required': True, 'placeholder': 'Say something...'}
            ),
        }