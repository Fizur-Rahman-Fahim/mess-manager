from decimal import Decimal

from django.conf import settings
from django.db import models


class DailyMeal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_meals',
    )
    date = models.DateField()
    breakfast = models.BooleanField(default=True)
    lunch = models.BooleanField(default=True)
    dinner = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['date']
        verbose_name = 'daily meal'
        verbose_name_plural = 'daily meals'

    def __str__(self):
        return f'{self.user} — {self.date:%Y-%m-%d}'

    def total_meal_value(self):
        from mess_core.models import MessSettings

        mess_settings = MessSettings.objects.first()
        if not mess_settings:
            return Decimal('0')

        total = Decimal('0')
        if self.breakfast:
            total += mess_settings.breakfast_meal_value
        if self.lunch:
            total += mess_settings.lunch_meal_value
        if self.dinner:
            total += mess_settings.dinner_meal_value
        return total
