from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _


class DepositClaimForm(forms.Form):
    amount = forms.DecimalField(
        label=_('Amount (৳)'),
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
    )
    date_claimed = forms.DateField(
        label=_('Date'),
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    note = forms.CharField(
        label=_('Note (optional)'),
        max_length=255,
        required=False,
        widget=forms.TextInput(),
    )
