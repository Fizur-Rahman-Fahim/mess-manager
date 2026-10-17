from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from expenses.models import BazarExpense


class BazarExpenseForm(forms.ModelForm):
    class Meta:
        model = BazarExpense
        fields = ('bazar_type', 'amount', 'date', 'description', 'receipt_image')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(),
        }
        labels = {
            'bazar_type': _('Bazar type'),
            'amount': _('Amount (৳)'),
            'date': _('Date'),
            'description': _('Description (optional)'),
            'receipt_image': _('Receipt (optional)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].min_value = Decimal('0.01')
