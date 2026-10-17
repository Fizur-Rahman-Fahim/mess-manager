from django.conf import settings
from django.db import models


class BazarExpense(models.Model):
    BAZAR_BORO = 'boro'
    BAZAR_CHOTO = 'choto'

    BAZAR_TYPE_CHOICES = [
        (BAZAR_BORO, 'বড় বাজার'),
        (BAZAR_CHOTO, 'ছোট বাজার'),
    ]

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bazar_expenses',
    )
    bazar_type = models.CharField(max_length=10, choices=BAZAR_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt_image = models.ImageField(upload_to='bazar_receipts/', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    month = models.DateField(help_text='First day of month (YYYY-MM-01) for aggregation.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'bazar expense'
        verbose_name_plural = 'bazar expenses'

    def __str__(self):
        return f'{self.get_bazar_type_display()} — ৳{self.amount} ({self.date:%Y-%m-%d})'

    @property
    def bazar_type_display_bn(self):
        if self.bazar_type == self.BAZAR_BORO:
            return 'বড় বাজার'
        return 'ছোট বাজার'
