from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from deposits.models import Deposit
from deposits.services.deposit import (
    approve_deposit,
    claim_deposit,
    count_pending_deposits,
    reject_deposit,
    sum_approved_deposits_for_user,
)

User = get_user_model()


class DepositServiceTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            mobile_number='01722222222',
            password='pass12345',
            full_name='Member',
            is_active_member=True,
        )
        self.manager = User.objects.create_user(
            mobile_number='01733333333',
            password='pass12345',
            full_name='Manager',
            is_active_member=True,
            is_super_manager=True,
        )

    def test_claim_creates_pending_deposit(self):
        deposit = claim_deposit(self.member, Decimal('500'), timezone.localdate())
        self.assertEqual(deposit.status, Deposit.STATUS_PENDING)
        self.assertEqual(count_pending_deposits(), 1)

    def test_claim_rejects_zero_amount(self):
        with self.assertRaises(ValidationError):
            claim_deposit(self.member, Decimal('0'), timezone.localdate())

    def test_approve_deposit(self):
        deposit = claim_deposit(self.member, Decimal('1000'), timezone.localdate())
        approve_deposit(deposit, self.manager)
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, Deposit.STATUS_APPROVED)
        self.assertEqual(deposit.approved_by, self.manager)

    def test_reject_deposit(self):
        deposit = claim_deposit(self.member, Decimal('500'), timezone.localdate())
        reject_deposit(deposit, self.manager)
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, Deposit.STATUS_REJECTED)

    def test_cannot_approve_twice(self):
        deposit = claim_deposit(self.member, Decimal('500'), timezone.localdate())
        approve_deposit(deposit, self.manager)
        with self.assertRaises(ValidationError):
            approve_deposit(deposit, self.manager)

    def test_sum_approved_deposits_for_month(self):
        today = timezone.localdate()
        month_str = f'{today.year:04d}-{today.month:02d}'
        d1 = claim_deposit(self.member, Decimal('500'), today)
        d2 = claim_deposit(self.member, Decimal('300'), today)
        approve_deposit(d1, self.manager)
        approve_deposit(d2, self.manager)
        total = sum_approved_deposits_for_user(self.member, month_str)
        self.assertEqual(total, Decimal('800'))
