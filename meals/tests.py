from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from meals.models import DailyMeal
from meals.services.meal import (
    is_meal_off_blocked_for_date,
    monthly_meal_count_for_user,
    toggle_meals,
    validate_meal_update,
)
from mess_core.models import MessSettings

User = get_user_model()


class MealServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            mobile_number='01711111111',
            password='pass12345',
            full_name='Test User',
            is_active_member=True,
        )
        MessSettings.objects.all().delete()
        MessSettings.objects.create(meal_off_cutoff_time=time(22, 0))

    def test_toggle_meals_updates_row(self):
        target = timezone.localdate() + timedelta(days=3)
        meal = toggle_meals(self.user, target, False, True, True)
        self.assertFalse(meal.breakfast)
        self.assertTrue(meal.lunch)

    def test_cannot_change_past_dates(self):
        past = timezone.localdate() - timedelta(days=1)
        DailyMeal.objects.create(user=self.user, date=past, breakfast=True, lunch=True, dinner=True)
        meal = DailyMeal.objects.get(user=self.user, date=past)
        with self.assertRaises(ValidationError):
            validate_meal_update(meal, False, True, True)

    @patch('meals.services.meal.is_past_cutoff', return_value=True)
    def test_cutoff_blocks_meal_off_today(self, _mock):
        today = timezone.localdate()
        meal = DailyMeal.objects.create(
            user=self.user, date=today, breakfast=True, lunch=True, dinner=True
        )
        with self.assertRaises(ValidationError):
            validate_meal_update(meal, False, True, True)

    @patch('meals.services.meal.is_past_cutoff', return_value=True)
    def test_cutoff_allows_meal_on(self, _mock):
        today = timezone.localdate()
        meal = DailyMeal.objects.create(
            user=self.user, date=today, breakfast=False, lunch=True, dinner=True
        )
        validate_meal_update(meal, True, True, True)

    def test_monthly_meal_count_defaults_missing_days(self):
        today = timezone.localdate()
        month_str = f'{today.year:04d}-{today.month:02d}'
        DailyMeal.objects.create(
            user=self.user,
            date=today,
            breakfast=True,
            lunch=False,
            dinner=True,
        )
        total = monthly_meal_count_for_user(self.user, month_str)
        self.assertGreater(total, Decimal('1.5'))

    def test_is_meal_off_blocked_only_today_tomorrow(self):
        today = timezone.localdate()
        with patch('meals.services.meal.is_past_cutoff', return_value=True):
            self.assertTrue(is_meal_off_blocked_for_date(today))
            self.assertTrue(is_meal_off_blocked_for_date(today + timedelta(days=1)))
            self.assertFalse(is_meal_off_blocked_for_date(today + timedelta(days=2)))
