from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = ('mobile_number', 'full_name')

    def clean_mobile_number(self):
        mobile = self.cleaned_data['mobile_number'].strip()
        if not mobile.isdigit() or len(mobile) < 10:
            raise ValidationError(_('Enter a valid mobile number (at least 10 digits).'))
        return mobile

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError(_('Passwords do not match.'))
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active_member = False
        if commit:
            user.save()
        return user


class MobileAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Mobile number'),
        max_length=15,
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )

    def clean(self):
        mobile = self.cleaned_data.get('username')
        if mobile:
            self.cleaned_data['username'] = mobile.strip()
        return super().clean()
