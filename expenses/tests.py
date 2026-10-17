from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from expenses.models import BazarExpense
from expenses.services.expense import (
    add_bazar_expense,
    calculate_meal_rate,
    monthly_breakdown,
    monthly_total,
)
from expenses.validators import validate_receipt_image
from meals.models import DailyMeal
from mess_core.models import MessSettings

User = get_user_model()


class ExpenseServiceTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            mobile_number='01744444444',
            password='pass12345',
            full_name='Manager',
            is_active_member=True,
            is_super_manager=True,
        )
        self.member = User.objects.create_user(
            mobile_number='01755555555',
            password='pass12345',
            full_name='Member',
            is_active_member=True,
        )
        MessSettings.objects.all().delete()
        MessSettings.objects.create()

    def test_add_bazar_expense(self):
        today = timezone.localdate()
        expense = add_bazar_expense(
            self.manager,
            BazarExpense.BAZAR_BORO,
            Decimal('1500'),
            today,
            description='Rice and oil',
        )
        self.assertEqual(expense.month, today.replace(day=1))
        self.assertEqual(expense.amount, Decimal('1500'))

    def test_monthly_total_and_breakdown(self):
        today = timezone.localdate()
        month_str = f'{today.year:04d}-{today.month:02d}'
        add_bazar_expense(self.manager, BazarExpense.BAZAR_BORO, Decimal('1000'), today)
        add_bazar_expense(self.manager, BazarExpense.BAZAR_CHOTO, Decimal('500'), today)

        self.assertEqual(monthly_total(month_str), Decimal('1500'))
        breakdown = monthly_breakdown(month_str)
        self.assertEqual(breakdown['boro_total'], Decimal('1000'))
        self.assertEqual(breakdown['choto_total'], Decimal('500'))

    def test_calculate_meal_rate(self):
        today = timezone.localdate()
        month_str = f'{today.year:04d}-{today.month:02d}'
        add_bazar_expense(self.manager, BazarExpense.BAZAR_BORO, Decimal('1000'), today)
        DailyMeal.objects.create(
            user=self.member,
            date=today,
            breakfast=True,
            lunch=True,
            dinner=True,
        )
        rate = calculate_meal_rate(month_str)
        self.assertGreater(rate, Decimal('0'))

    def test_reject_zero_amount(self):
        with self.assertRaises(ValidationError):
            add_bazar_expense(
                self.manager,
                BazarExpense.BAZAR_BORO,
                Decimal('0'),
                timezone.localdate(),
            )

    def test_reject_invalid_receipt_extension(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        bad_file = SimpleUploadedFile('receipt.pdf', b'fake', content_type='application/pdf')
        with self.assertRaises(ValidationError):
            validate_receipt_image(bad_file)
