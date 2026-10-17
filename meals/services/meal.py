import calendar
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mess_core.models import MessSettings
from meals.models import DailyMeal

User = get_user_model()


def get_mess_settings():
    settings_obj = MessSettings.objects.first()
    if not settings_obj:
        settings_obj = MessSettings.objects.create()
    return settings_obj


def parse_month(month_str: str) -> tuple[date, date]:
    """Parse YYYY-MM into (first_day, last_day) of that month."""
    try:
        year, month = map(int, month_str.split('-'))
        if month < 1 or month > 12:
            raise ValueError
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)
    except (ValueError, AttributeError):
        raise ValidationError(_('Invalid month format. Use YYYY-MM (e.g. 2026-08).'))


def current_month_str() -> str:
    today = timezone.localdate()
    return f'{today.year:04d}-{today.month:02d}'


def is_past_cutoff() -> bool:
    now = timezone.localtime()
    cutoff = get_mess_settings().meal_off_cutoff_time
    return now.time() >= cutoff


def is_meal_off_blocked_for_date(target_date: date) -> bool:
    """After cutoff, meal-off for today or tomorrow is blocked."""
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    if target_date not in (today, tomorrow):
        return False
    return is_past_cutoff()


def can_modify_date(target_date: date) -> bool:
    """Members cannot change meals for past dates."""
    return target_date >= timezone.localdate()


def get_or_create_daily_meal(user, target_date: date) -> DailyMeal:
    meal, _ = DailyMeal.objects.get_or_create(
        user=user,
        date=target_date,
        defaults={'breakfast': True, 'lunch': True, 'dinner': True},
    )
    return meal


def validate_meal_update(daily_meal: DailyMeal, breakfast: bool, lunch: bool, dinner: bool):
    if not can_modify_date(daily_meal.date):
        raise ValidationError(_('Cannot change meals for past dates.'))

    if is_meal_off_blocked_for_date(daily_meal.date):
        if breakfast is False and daily_meal.breakfast:
            raise ValidationError(
                _('Meal off is not allowed after cutoff time for today or tomorrow.')
            )
        if lunch is False and daily_meal.lunch:
            raise ValidationError(
                _('Meal off is not allowed after cutoff time for today or tomorrow.')
            )
        if dinner is False and daily_meal.dinner:
            raise ValidationError(
                _('Meal off is not allowed after cutoff time for today or tomorrow.')
            )


def toggle_meals(user, target_date: date, breakfast: bool, lunch: bool, dinner: bool) -> DailyMeal:
    daily_meal = get_or_create_daily_meal(user, target_date)
    validate_meal_update(daily_meal, breakfast, lunch, dinner)
    daily_meal.breakfast = breakfast
    daily_meal.lunch = lunch
    daily_meal.dinner = dinner
    daily_meal.save(update_fields=['breakfast', 'lunch', 'dinner'])
    return daily_meal


def get_user_meals_for_month(user, month_str: str) -> list[DailyMeal]:
    start, end = parse_month(month_str)
    existing = {
        m.date: m
        for m in DailyMeal.objects.filter(user=user, date__gte=start, date__lte=end)
    }
    meals = []
    current = start
    while current <= end:
        if current in existing:
            meals.append(existing[current])
        else:
            meals.append(
                DailyMeal(
                    user=user,
                    date=current,
                    breakfast=True,
                    lunch=True,
                    dinner=True,
                )
            )
        current += timedelta(days=1)
    return meals


def monthly_meal_count_for_user(user, month_str: str) -> Decimal:
    start, end = parse_month(month_str)
    meals = DailyMeal.objects.filter(user=user, date__gte=start, date__lte=end)
    total = Decimal('0')
    for meal in meals:
        total += meal.total_meal_value()

    # Default-all-True for days without rows in range
    mess_settings = get_mess_settings()
    default_per_day = (
        mess_settings.breakfast_meal_value
        + mess_settings.lunch_meal_value
        + mess_settings.dinner_meal_value
    )
    days_with_rows = meals.count()
    total_days = (end - start).days + 1
    missing_days = max(0, total_days - days_with_rows)
    total += default_per_day * missing_days
    return total


def total_meal_count_for_month(month_str: str) -> Decimal:
    """Sum of meal values across all active members for a month."""
    members = User.objects.filter(is_active_member=True)
    total = Decimal('0')
    for member in members:
        total += monthly_meal_count_for_user(member, month_str)
    return total


def get_monthly_summary(month_str: str) -> list[dict]:
    """Per-member meal breakdown for managers."""
    members = User.objects.filter(is_active_member=True).order_by('full_name')
    summary = []
    for member in members:
        start, end = parse_month(month_str)
        total_days = (end - start).days + 1
        meals = DailyMeal.objects.filter(user=member, date__gte=start, date__lte=end)
        row_count = meals.count()
        missing_days = max(0, total_days - row_count)
        breakfast_count = meals.filter(breakfast=True).count() + missing_days
        lunch_count = meals.filter(lunch=True).count() + missing_days
        dinner_count = meals.filter(dinner=True).count() + missing_days
        meal_value = monthly_meal_count_for_user(member, month_str)
        summary.append(
            {
                'user_id': member.id,
                'full_name': member.full_name,
                'mobile_number': member.mobile_number,
                'breakfast_count': breakfast_count,
                'lunch_count': lunch_count,
                'dinner_count': dinner_count,
                'total_meal_value': meal_value,
            }
        )
    return summary


def get_daily_meal_summary(month_str: str) -> list[dict]:
    """Return daily on/off counts and member statuses for managers."""
    start, end = parse_month(month_str)
    members = list(User.objects.filter(is_active_member=True).order_by('full_name'))
    meals_by_user_date = {
        (meal.user_id, meal.date): meal
        for meal in DailyMeal.objects.filter(
            user__in=members,
            date__gte=start,
            date__lte=end,
        )
    }

    daily_summary = []
    current = start
    while current <= end:
        member_statuses = []
        for member in members:
            meal = meals_by_user_date.get((member.id, current))
            member_statuses.append(
                {
                    'user_id': member.id,
                    'full_name': member.full_name,
                    'mobile_number': member.mobile_number,
                    'breakfast': meal.breakfast if meal else True,
                    'lunch': meal.lunch if meal else True,
                    'dinner': meal.dinner if meal else True,
                }
            )

        daily_summary.append(
            {
                'date': current,
                'breakfast_on': sum(status['breakfast'] for status in member_statuses),
                'breakfast_off': sum(not status['breakfast'] for status in member_statuses),
                'lunch_on': sum(status['lunch'] for status in member_statuses),
                'lunch_off': sum(not status['lunch'] for status in member_statuses),
                'dinner_on': sum(status['dinner'] for status in member_statuses),
                'dinner_off': sum(not status['dinner'] for status in member_statuses),
                'members': member_statuses,
            }
        )
        current += timedelta(days=1)

    return daily_summary


def create_default_meals_for_active_members(days_ahead: int = 30) -> int:
    """Create default all-on meal rows for active members."""
    today = timezone.localdate()
    end = today + timedelta(days=days_ahead)
    members = User.objects.filter(is_active_member=True)
    created = 0

    for member in members:
        current = today
        while current <= end:
            _, was_created = DailyMeal.objects.get_or_create(
                user=member,
                date=current,
                defaults={'breakfast': True, 'lunch': True, 'dinner': True},
            )
            if was_created:
                created += 1
            current += timedelta(days=1)
    return created
