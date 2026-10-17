from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Complaint


def create_complaint(user, title: str, description: str) -> Complaint:
    if not title.strip() or not description.strip():
        raise ValidationError('Title and description are required.')
    return Complaint.objects.create(
        raised_by=user,
        title=title.strip(),
        description=description.strip(),
    )


def update_complaint_status(complaint: Complaint, status: str, handled_by) -> Complaint:
    valid_statuses = {choice[0] for choice in Complaint.STATUS_CHOICES}
    if status not in valid_statuses:
        raise ValidationError('Invalid complaint status.')
    complaint.status = status
    complaint.handled_by = handled_by
    complaint.resolved_at = timezone.now() if status == Complaint.STATUS_RESOLVED else None
    complaint.save(update_fields=['status', 'handled_by', 'resolved_at'])
    return complaint
