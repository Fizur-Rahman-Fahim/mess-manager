from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from decimal import Decimal

from mess_core.models import MessSettings, MonthlyManagerAssignment
from mess_core.services.fixed_meal import billable_meal_count_for_user, set_fixed_meal
from mess_core.services.manager import assign_monthly_manager

User = get_user_model()


class ManagerAssignmentTests(TestCase):
	def setUp(self):
		self.super_manager = User.objects.create_superuser(
			mobile_number='01700000001',
			full_name='Super Manager',
			password='pass12345',
		)
		self.first_member = User.objects.create_user(
			mobile_number='01700000002',
			full_name='First Member',
			password='pass12345',
			is_active_member=True,
		)
		self.second_member = User.objects.create_user(
			mobile_number='01700000003',
			full_name='Second Member',
			password='pass12345',
			is_active_member=True,
		)

	def test_reassignment_closes_previous_manager(self):
		first = assign_monthly_manager(self.first_member.id, '2026-08', self.super_manager)
		second = assign_monthly_manager(self.second_member.id, '2026-09', self.super_manager)

		first.refresh_from_db()
		self.assertFalse(first.is_active)
		self.assertIsNotNone(first.end_date)
		self.assertTrue(second.is_active)
		self.assertEqual(MonthlyManagerAssignment.objects.filter(is_active=True).count(), 1)

	def test_inactive_user_cannot_be_assigned(self):
		inactive = User.objects.create_user(
			mobile_number='01700000004', full_name='Inactive', password='pass12345'
		)
		with self.assertRaises(ValidationError):
			assign_monthly_manager(inactive.id, '2026-08', self.super_manager)

	def test_settings_is_singleton(self):
		self.assertEqual(MessSettings.objects.count(), 1)
		with self.assertRaises(ValidationError):
			MessSettings.objects.create()

	def test_fixed_meal_is_a_global_monthly_minimum(self):
		set_fixed_meal('2026-08', Decimal('100'), self.super_manager)
		self.assertEqual(billable_meal_count_for_user(self.first_member, '2026-08'), Decimal('100'))

		set_fixed_meal('2026-08', Decimal('1'), self.super_manager)
		self.assertGreater(billable_meal_count_for_user(self.first_member, '2026-08'), Decimal('1'))

# Create your tests here.
