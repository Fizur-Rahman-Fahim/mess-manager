from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from deposits.models import Deposit
from meals.services.meal import parse_month

User = get_user_model()


def claim_deposit(user, amount: Decimal, date_claimed, note: str = '') -> Deposit:
    if amount <= 0:
        raise ValidationError(_('Deposit amount must be greater than zero.'))

    return Deposit.objects.create(
        user=user,
        amount=amount,
        date_claimed=date_claimed,
        note=note.strip(),
        status=Deposit.STATUS_PENDING,
    )


def approve_deposit(deposit: Deposit, approved_by) -> Deposit:
    if deposit.status != Deposit.STATUS_PENDING:
        raise ValidationError(_('Only pending deposits can be approved.'))

    deposit.status = Deposit.STATUS_APPROVED
    deposit.approved_by = approved_by
    deposit.approved_at = timezone.now()
    deposit.save(update_fields=['status', 'approved_by', 'approved_at'])
    return deposit


def reject_deposit(deposit: Deposit, approved_by) -> Deposit:
    if deposit.status != Deposit.STATUS_PENDING:
        raise ValidationError(_('Only pending deposits can be rejected.'))

    deposit.status = Deposit.STATUS_REJECTED
    deposit.approved_by = approved_by
    deposit.approved_at = timezone.now()
    deposit.save(update_fields=['status', 'approved_by', 'approved_at'])
    return deposit


def get_pending_deposits():
    return Deposit.objects.filter(status=Deposit.STATUS_PENDING).select_related('user')


def count_pending_deposits() -> int:
    return Deposit.objects.filter(status=Deposit.STATUS_PENDING).count()


def get_user_deposits(user, month_str: str | None = None):
    queryset = Deposit.objects.filter(user=user)
    if month_str:
        start, end = parse_month(month_str)
        queryset = queryset.filter(date_claimed__gte=start, date_claimed__lte=end)
    return queryset


def sum_approved_deposits_for_user(user, month_str: str) -> Decimal:
    start, end = parse_month(month_str)
    result = Deposit.objects.filter(
        user=user,
        status=Deposit.STATUS_APPROVED,
        date_claimed__gte=start,
        date_claimed__lte=end,
    ).aggregate(total=Sum('amount'))
    return result['total'] or Decimal('0')
