from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from deposits.services.deposit import count_pending_deposits
from complaints.models import Complaint
from bills.services.bill import get_user_bill
from expenses.services.expense import monthly_total
from meals.services.meal import current_month_str, monthly_meal_count_for_user
from mess_core.services.manager import get_active_manager


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        can_manage = (
            user.is_super_manager or user.is_superuser or user.is_monthly_manager
        )
        context['can_manage_deposits'] = can_manage
        context['can_manage_expenses'] = can_manage
        context['pending_deposits_count'] = count_pending_deposits() if can_manage else 0
        context['my_complaints_count'] = Complaint.objects.filter(raised_by=user).count()
        context['pending_complaints_count'] = (
            Complaint.objects.filter(status=Complaint.STATUS_PENDING).count() if can_manage else 0
        )
        month = current_month_str()
        context['current_month'] = month
        context['meal_count'] = monthly_meal_count_for_user(user, month)
        context['my_bill'] = get_user_bill(user, month)
        context['monthly_expense_total'] = monthly_total(month) if can_manage else 0
        context['active_manager'] = get_active_manager()
        return context
