from django.contrib.auth import get_user_model

User = get_user_model()


def approve_member(user, approved_by=None):
    """Activate a pending member after super manager approval."""
    user.is_active_member = True
    user.save(update_fields=['is_active_member'])
    return user


def get_pending_members():
    return User.objects.filter(is_active_member=False, is_superuser=False).order_by('date_joined')


def count_active_members():
    return User.objects.filter(is_active_member=True).count()
