from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from bills.models import UserBillRecord
from bills.services.bill import (
    equal_share,
    generate_bills,
    get_user_bill,
    set_electricity,
    set_house_rent,
)
from deposits.services.deposit import approve_deposit, claim_deposit
from expenses.models import BazarExpense
from expenses.services.expense import add_bazar_expense
from meals.models import DailyMeal
from mess_core.models import MessSettings

User = get_user_model()


class BillServiceTests(TestCase):
    def setUp(self):
        self.member_a = User.objects.create_user(
            mobile_number='01811111111',
            password='pass12345',
            full_name='Member A',
            is_active_member=True,
        )
        self.member_b = User.objects.create_user(
            mobile_number='01822222222',
            password='pass12345',
            full_name='Member B',
            is_active_member=True,
        )
        self.manager = User.objects.create_user(
            mobile_number='01833333333',
            password='pass12345',
            full_name='Manager',
            is_active_member=True,
            is_super_manager=True,
        )
        MessSettings.objects.all().delete()
        MessSettings.objects.create(
            seat_bill_default=Decimal('1150.00'),
            current_bill_default=Decimal('300.00'),
            breakfast_meal_value=Decimal('0.50'),
            lunch_meal_value=Decimal('1.00'),
            dinner_meal_value=Decimal('1.00'),
        )
        self.today = timezone.localdate()
        self.month_str = f'{self.today.year:04d}-{self.today.month:02d}'

    def test_equal_share(self):
        self.assertEqual(equal_share(Decimal('300'), 2), Decimal('150.00'))
        self.assertEqual(equal_share(Decimal('100'), 0), Decimal('0'))

    def test_set_house_rent_and_electricity(self):
        cycle = set_house_rent(
            self.month_str, Decimal('10000'), Decimal('2000'), set_by=self.manager
        )
        cycle = set_electricity(
            self.month_str, Decimal('2000'), Decimal('500'), set_by=self.manager
        )
        self.assertEqual(cycle.house_rent_total, Decimal('10000'))
        self.assertEqual(cycle.house_rent_paid, Decimal('2000'))
        self.assertEqual(cycle.electricity_bill_total, Decimal('2000'))
        self.assertEqual(cycle.electricity_bill_paid, Decimal('500'))

    def test_generate_rejects_when_no_active_members(self):
        User.objects.filter(is_active_member=True).update(is_active_member=False)
        with self.assertRaises(ValidationError):
            generate_bills(self.month_str, generated_by=self.manager)

    def test_generate_bills_math(self):
        # 3 active members (A, B, manager). Rent 3000 → 1000 each. Electricity 600 → 200 each.
        # Current bill 300 → 100 each. Seat 1150.
        set_house_rent(self.month_str, Decimal('3000'), set_by=self.manager)
        set_electricity(self.month_str, Decimal('600'), set_by=self.manager)

        add_bazar_expense(
            self.manager,
            BazarExpense.BAZAR_BORO,
            Decimal('250'),
            self.today,
        )
        DailyMeal.objects.create(
            user=self.member_a,
            date=self.today,
            breakfast=True,
            lunch=True,
            dinner=True,
        )

        deposit = claim_deposit(self.member_a, Decimal('5000'), self.today)
        approve_deposit(deposit, self.manager)

        generate_bills(self.month_str, generated_by=self.manager)

        bill = get_user_bill(self.member_a, self.month_str)
        self.assertIsNotNone(bill)
        self.assertEqual(bill.seat_bill, Decimal('1150.00'))
        self.assertEqual(bill.current_bill_share, Decimal('100.00'))
        self.assertEqual(bill.house_rent_share, Decimal('1000.00'))
        self.assertEqual(bill.electricity_share, Decimal('200.00'))
        self.assertEqual(bill.total_deposit, Decimal('5000'))
        expected_due = (
            bill.seat_bill
            + bill.current_bill_share
            + bill.house_rent_share
            + bill.electricity_share
            + bill.meal_cost
        )
        self.assertEqual(bill.total_due, expected_due)
        self.assertEqual(bill.balance, bill.total_deposit - bill.total_due)
        self.assertGreater(bill.meal_cost, Decimal('0'))
        self.assertEqual(UserBillRecord.objects.filter(month=self.today.replace(day=1)).count(), 3)
