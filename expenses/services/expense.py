from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from expenses.models import BazarExpense
from expenses.validators import validate_receipt_image
from meals.services.meal import parse_month, total_meal_count_for_month


def month_from_date(date_value):
    return date_value.replace(day=1)


def add_bazar_expense(
    user,
    bazar_type: str,
    amount: Decimal,
    date,
    description: str = '',
    receipt_image=None,
) -> BazarExpense:
    if amount <= 0:
        raise ValidationError(_('Expense amount must be greater than zero.'))

    if bazar_type not in (BazarExpense.BAZAR_BORO, BazarExpense.BAZAR_CHOTO):
        raise ValidationError(_('Invalid bazar type.'))

    validate_receipt_image(receipt_image)

    return BazarExpense.objects.create(
        added_by=user,
        bazar_type=bazar_type,
        amount=amount,
        date=date,
        description=description.strip(),
        month=month_from_date(date),
        receipt_image=receipt_image,
    )


def get_expenses_for_month(month_str: str):
    month_start, _ = parse_month(month_str)
    return BazarExpense.objects.filter(month=month_start).select_related('added_by')


def monthly_total(month_str: str) -> Decimal:
    month_start, _ = parse_month(month_str)
    result = BazarExpense.objects.filter(month=month_start).aggregate(total=Sum('amount'))
    return result['total'] or Decimal('0')


def monthly_breakdown(month_str: str) -> dict:
    month_start, _ = parse_month(month_str)
    expenses = BazarExpense.objects.filter(month=month_start)
    boro = expenses.filter(bazar_type=BazarExpense.BAZAR_BORO).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    choto = expenses.filter(bazar_type=BazarExpense.BAZAR_CHOTO).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    total = boro + choto
    return {
        'boro_total': boro,
        'choto_total': choto,
        'total': total,
    }


def calculate_meal_rate(month_str: str) -> Decimal:
    """Meal rate = total bazar expense ÷ total meal count for the month."""
    total_bazar = monthly_total(month_str)
    meal_count = total_meal_count_for_month(month_str)
    if meal_count == 0:
        return Decimal('0')
    return (total_bazar / meal_count).quantize(Decimal('0.01'))


def get_monthly_expense_summary(month_str: str) -> dict:
    breakdown = monthly_breakdown(month_str)
    meal_count = total_meal_count_for_month(month_str)
    meal_rate = calculate_meal_rate(month_str)
    return {
        'month': month_str,
        'expenses': list(get_expenses_for_month(month_str)),
        'boro_total': breakdown['boro_total'],
        'choto_total': breakdown['choto_total'],
        'total_bazar': breakdown['total'],
        'total_meal_count': meal_count,
        'meal_rate': meal_rate,
    }
