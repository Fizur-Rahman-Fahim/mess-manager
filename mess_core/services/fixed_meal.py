from decimal import Decimal

from django.core.exceptions import ValidationError

from meals.services.meal import monthly_meal_count_for_user, parse_month
from mess_core.models import MonthlyFixedMeal


def get_fixed_meal(month_str: str):
    month_start, _month_end = parse_month(month_str)
    return MonthlyFixedMeal.objects.filter(month=month_start).first()


def set_fixed_meal(month_str: str, fixed_meal_count: Decimal, set_by=None):
    if fixed_meal_count < 0:
        raise ValidationError('Fixed meal count cannot be negative.')
    month_start, _month_end = parse_month(month_str)
    fixed_meal, _created = MonthlyFixedMeal.objects.update_or_create(
        month=month_start,
        defaults={'fixed_meal_count': fixed_meal_count, 'set_by': set_by},
    )
    return fixed_meal


def billable_meal_count_for_user(user, month_str: str) -> Decimal:
    actual = monthly_meal_count_for_user(user, month_str)
    fixed_meal = get_fixed_meal(month_str)
    minimum = fixed_meal.fixed_meal_count if fixed_meal else Decimal('0')
    return max(actual, minimum)
