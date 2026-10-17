from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _


class HouseRentForm(forms.Form):
    total = forms.DecimalField(
        label=_('House rent total (৳)'),
        min_value=Decimal('0'),
        max_digits=10,
        decimal_places=2,
    )
    paid = forms.DecimalField(
        label=_('Paid amount (৳)'),
        min_value=Decimal('0'),
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal('0'),
    )


class ElectricityForm(forms.Form):
    total = forms.DecimalField(
        label=_('Electricity bill total (৳)'),
        min_value=Decimal('0'),
        max_digits=10,
        decimal_places=2,
    )
    paid = forms.DecimalField(
        label=_('Paid amount (৳)'),
        min_value=Decimal('0'),
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal('0'),
    )
