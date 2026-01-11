from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Status

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ('name',)
        labels = {'name': _('Name')}
