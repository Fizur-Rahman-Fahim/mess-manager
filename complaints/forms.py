from django import forms

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('title', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded border px-3 py-2'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded border px-3 py-2', 'rows': 5}),
        }
