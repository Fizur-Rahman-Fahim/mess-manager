from rest_framework.permissions import BasePermission


class IsActiveMember(BasePermission):
    message = 'Your account is pending approval.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_super_manager:
            return True
        return request.user.is_active_member


class IsSuperManager(BasePermission):
    message = 'Super Manager access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_super_manager or request.user.is_superuser)
        )


class IsMonthlyManagerOrAbove(BasePermission):
    message = 'Monthly Manager or Super Manager access required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_super_manager or request.user.is_superuser:
            return True
        return request.user.is_monthly_manager and request.user.is_active_member
