from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.services.member import count_active_members
from bills.models import MonthlyBillCycle, UserBillRecord
from deposits.services.deposit import sum_approved_deposits_for_user
from expenses.services.expense import calculate_meal_rate
from meals.services.meal import (
    get_mess_settings,
    parse_month,
)
from mess_core.services.fixed_meal import billable_meal_count_for_user

User = get_user_model()


def equal_share(total: Decimal, member_count: int) -> Decimal:
    if member_count == 0:
        return Decimal('0')
    return (total / member_count).quantize(Decimal('0.01'))


def get_or_create_cycle(month_str: str, set_by=None) -> MonthlyBillCycle:
    month_start, _month_end = parse_month(month_str)
    cycle, _ = MonthlyBillCycle.objects.get_or_create(
        month=month_start,
        defaults={'set_by': set_by},
    )
    return cycle


def get_cycle(month_str: str) -> MonthlyBillCycle | None:
    month_start, _month_end = parse_month(month_str)
    return MonthlyBillCycle.objects.filter(month=month_start).first()


def set_house_rent(
    month_str: str,
    total: Decimal,
    paid: Decimal = Decimal('0'),
    set_by=None,
) -> MonthlyBillCycle:
    if total < 0 or paid < 0:
        raise ValidationError(_('Amounts cannot be negative.'))

    cycle = get_or_create_cycle(month_str, set_by)
    cycle.house_rent_total = total
    cycle.house_rent_paid = paid
    if set_by:
        cycle.set_by = set_by
    cycle.save(update_fields=['house_rent_total', 'house_rent_paid', 'set_by', 'updated_at'])
    return cycle


def set_electricity(
    month_str: str,
    total: Decimal,
    paid: Decimal = Decimal('0'),
    set_by=None,
) -> MonthlyBillCycle:
    if total < 0 or paid < 0:
        raise ValidationError(_('Amounts cannot be negative.'))

    cycle = get_or_create_cycle(month_str, set_by)
    cycle.electricity_bill_total = total
    cycle.electricity_bill_paid = paid
    if set_by:
        cycle.set_by = set_by
    cycle.save(
        update_fields=['electricity_bill_total', 'electricity_bill_paid', 'set_by', 'updated_at']
    )
    return cycle


def generate_bills(month_str: str, generated_by=None) -> MonthlyBillCycle:
    month_start, _month_end = parse_month(month_str)
    member_count = count_active_members()
    if member_count == 0:
        raise ValidationError(_('No active members to generate bills for.'))

    cycle = get_or_create_cycle(month_str, generated_by)
    meal_count = sum(
        (billable_meal_count_for_user(member, month_str) for member in User.objects.filter(is_active_member=True)),
        Decimal('0'),
    )
    meal_rate = calculate_meal_rate(month_str)

    cycle.total_meal_count = meal_count
    cycle.meal_rate = meal_rate
    if generated_by:
        cycle.set_by = generated_by
    cycle.save(
        update_fields=['total_meal_count', 'meal_rate', 'set_by', 'updated_at']
    )

    mess_settings = get_mess_settings()
    members = User.objects.filter(is_active_member=True)

    current_share = equal_share(mess_settings.current_bill_default, member_count)
    rent_share = equal_share(cycle.house_rent_total, member_count)
    electricity_share = equal_share(cycle.electricity_bill_total, member_count)
    seat_bill = mess_settings.seat_bill_default

    for member in members:
        user_meal_count = billable_meal_count_for_user(member, month_str)
        meal_cost = (user_meal_count * meal_rate).quantize(Decimal('0.01'))
        total_deposit = sum_approved_deposits_for_user(member, month_str)
        total_due = seat_bill + current_share + rent_share + electricity_share + meal_cost
        balance = total_deposit - total_due

        UserBillRecord.objects.update_or_create(
            user=member,
            month=month_start,
            defaults={
                'seat_bill': seat_bill,
                'current_bill_share': current_share,
                'house_rent_share': rent_share,
                'electricity_share': electricity_share,
                'meal_cost': meal_cost,
                'total_due': total_due,
                'total_deposit': total_deposit,
                'balance': balance,
            },
        )

    return cycle


def get_user_bill(user, month_str: str) -> UserBillRecord | None:
    month_start, _ = parse_month(month_str)
    return UserBillRecord.objects.filter(user=user, month=month_start).first()


def get_all_bills_for_month(month_str: str):
    month_start, _ = parse_month(month_str)
    return UserBillRecord.objects.filter(month=month_start).select_related('user').order_by(
        'user__full_name'
    )
