from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class MessSettings(models.Model):
    """Singleton-style global mess configuration."""

    seat_bill_default = models.DecimalField(max_digits=8, decimal_places=2, default=1150.00)
    current_bill_default = models.DecimalField(max_digits=8, decimal_places=2, default=300.00)
    breakfast_meal_value = models.DecimalField(max_digits=3, decimal_places=2, default=0.5)
    lunch_meal_value = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    dinner_meal_value = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    meal_off_cutoff_time = models.TimeField(default='22:00')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'mess settings'
        verbose_name_plural = 'mess settings'

    def __str__(self):
        return 'Mess Settings'

    def save(self, *args, **kwargs):
        if not self.pk and MessSettings.objects.exists():
            raise ValidationError(_('Only one MessSettings row is allowed.'))
        return super().save(*args, **kwargs)


class MonthlyManagerAssignment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monthly_manager_assignments',
    )
    month = models.DateField()
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assignments_made',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.user} — {self.month:%Y-%m}'

    def save(self, *args, **kwargs):
        if self.is_active:
            active = MonthlyManagerAssignment.objects.filter(is_active=True)
            if self.pk:
                active = active.exclude(pk=self.pk)
            if active.exists():
                raise ValidationError(_('Only one monthly manager can be active at a time.'))
        super().save(*args, **kwargs)


class MonthlyFixedMeal(models.Model):
    month = models.DateField(unique=True)
    fixed_meal_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    set_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fixed_meals_set',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month']

    def __str__(self):
        return f'{self.month:%Y-%m}: {self.fixed_meal_count}'
