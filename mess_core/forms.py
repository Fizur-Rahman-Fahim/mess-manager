from decimal import Decimal

from django import forms

from .models import MessSettings, MonthlyFixedMeal


class MessSettingsForm(forms.ModelForm):
    class Meta:
        model = MessSettings
        fields = (
            'seat_bill_default', 'current_bill_default', 'breakfast_meal_value',
            'lunch_meal_value', 'dinner_meal_value', 'meal_off_cutoff_time',
        )
        widgets = {'meal_off_cutoff_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'})}

    def clean(self):
        cleaned = super().clean()
        for field in ('seat_bill_default', 'current_bill_default', 'breakfast_meal_value', 'lunch_meal_value', 'dinner_meal_value'):
            if cleaned.get(field) is not None and cleaned[field] < Decimal('0'):
                self.add_error(field, 'Value cannot be negative.')
        return cleaned


class MonthlyFixedMealForm(forms.ModelForm):
    month = forms.DateField(widget=forms.DateInput(format='%Y-%m', attrs={'type': 'month'}), input_formats=['%Y-%m'])

    class Meta:
        model = MonthlyFixedMeal
        fields = ('month', 'fixed_meal_count')
        widgets = {'fixed_meal_count': forms.NumberInput(attrs={'min': '0', 'step': '0.01'})}

    def clean_fixed_meal_count(self):
        value = self.cleaned_data['fixed_meal_count']
        if value < 0:
            raise forms.ValidationError('Fixed meal count cannot be negative.')
        return value
