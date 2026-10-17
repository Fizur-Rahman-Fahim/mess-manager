from django.conf import settings
from django.db import models


class MonthlyBillCycle(models.Model):
    month = models.DateField(unique=True)
    house_rent_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    house_rent_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_bill_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_bill_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_meal_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    meal_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    set_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill_cycles_set',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month']
        verbose_name = 'monthly bill cycle'
        verbose_name_plural = 'monthly bill cycles'

    def __str__(self):
        return f'Bill cycle {self.month:%Y-%m}'


class UserBillRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bill_records',
    )
    month = models.DateField()
    seat_bill = models.DecimalField(max_digits=8, decimal_places=2)
    current_bill_share = models.DecimalField(max_digits=8, decimal_places=2)
    house_rent_share = models.DecimalField(max_digits=8, decimal_places=2)
    electricity_share = models.DecimalField(max_digits=8, decimal_places=2)
    meal_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    total_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']
        verbose_name = 'user bill record'
        verbose_name_plural = 'user bill records'

    def __str__(self):
        return f'{self.user} — {self.month:%Y-%m} (৳{self.total_due})'
