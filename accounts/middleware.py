from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class ActiveMemberMiddleware(MiddlewareMixin):
    """Redirect inactive members away from app pages (except auth and admin)."""

    EXEMPT_PREFIXES = (
        '/accounts/',
        '/admin/',
        '/api/auth/',
        '/static/',
        '/media/',
    )

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        path = request.path
        if any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return None

        if request.user.is_superuser or request.user.is_super_manager:
            return None

        if not request.user.is_active_member:
            if path != reverse('accounts:pending_approval'):
                return redirect('accounts:pending_approval')
        return None
