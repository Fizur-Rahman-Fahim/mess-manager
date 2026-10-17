from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as gettext

from meals.services.meal import parse_month
from mess_core.models import MonthlyManagerAssignment

User = get_user_model()


@transaction.atomic
def assign_monthly_manager(user_id: int, month_str: str, assigned_by=None):
    month_start, _month_end = parse_month(month_str)
    user = User.objects.filter(pk=user_id, is_active_member=True).first()
    if not user:
        raise ValidationError(gettext('Only an active member can become Monthly Manager.'))

    today = timezone.localdate()
    current = MonthlyManagerAssignment.objects.select_for_update().filter(is_active=True).first()
    if current:
        if current.user_id == user.id and current.month == month_start:
            return current
        current.is_active = False
        current.end_date = today
        current.save(update_fields=['is_active', 'end_date'])

    return MonthlyManagerAssignment.objects.create(
        user=user,
        month=month_start,
        assigned_by=assigned_by,
        is_active=True,
        start_date=today,
    )


def get_active_manager():
    return MonthlyManagerAssignment.objects.filter(is_active=True).select_related('user').first()
