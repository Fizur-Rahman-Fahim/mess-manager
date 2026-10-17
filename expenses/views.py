from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from expenses.forms import BazarExpenseForm
from expenses.mixins import ManagerRequiredMixin
from expenses.services.expense import add_bazar_expense, get_monthly_expense_summary
from meals.services.meal import current_month_str


class BazarListView(ManagerRequiredMixin, TemplateView):
    template_name = 'expenses/bazar_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            summary = get_monthly_expense_summary(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            summary = get_monthly_expense_summary(month)

        context.update(summary)
        return context


class BazarAddView(ManagerRequiredMixin, FormView):
    template_name = 'expenses/bazar_add.html'
    form_class = BazarExpenseForm
    success_url = reverse_lazy('expenses:bazar_list')

    def get_initial(self):
        return {'date': timezone.localdate()}

    def form_valid(self, form):
        try:
            add_bazar_expense(
                self.request.user,
                form.cleaned_data['bazar_type'],
                form.cleaned_data['amount'],
                form.cleaned_data['date'],
                form.cleaned_data.get('description', ''),
                form.cleaned_data.get('receipt_image'),
            )
            messages.success(self.request, 'বাজার খরচ যোগ করা হয়েছে।')
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            return self.form_invalid(form)
        return super().form_valid(form)
