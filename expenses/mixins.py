from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Monthly Manager or Super Manager."""

    def test_func(self):
        user = self.request.user
        return (
            user.is_super_manager
            or user.is_superuser
            or user.is_monthly_manager
        )

    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect

        messages.error(
            self.request,
            'Monthly Manager or Super Manager access required.',
        )
        return redirect('dashboard:home')
