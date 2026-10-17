from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, View

from bills.forms import ElectricityForm, HouseRentForm
from bills.services.bill import (
    generate_bills,
    get_all_bills_for_month,
    get_cycle,
    get_user_bill,
    set_electricity,
    set_house_rent,
)
from meals.services.meal import current_month_str


class SuperManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_super_manager or user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Super Manager access required.')
        return redirect('dashboard:home')


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return (
            user.is_super_manager
            or user.is_superuser
            or user.is_monthly_manager
        )

    def handle_no_permission(self):
        messages.error(self.request, 'Monthly Manager or Super Manager access required.')
        return redirect('dashboard:home')


class MyBillView(LoginRequiredMixin, TemplateView):
    template_name = 'bills/my_bill.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            bill = get_user_bill(self.request.user, month)
            cycle = get_cycle(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            bill = get_user_bill(self.request.user, month)
            cycle = get_cycle(month)

        context.update(
            {
                'month': month,
                'bill': bill,
                'cycle': cycle,
                'can_manage': self._can_manage(),
            }
        )
        return context

    def _can_manage(self):
        user = self.request.user
        return user.is_super_manager or user.is_superuser or user.is_monthly_manager


class BillManageView(SuperManagerRequiredMixin, TemplateView):
    template_name = 'bills/manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            cycle = get_cycle(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            cycle = get_cycle(month)

        context.update(
            {
                'month': month,
                'cycle': cycle,
                'house_rent_form': HouseRentForm(
                    initial={
                        'total': cycle.house_rent_total if cycle else 0,
                        'paid': cycle.house_rent_paid if cycle else 0,
                    }
                ),
                'electricity_form': ElectricityForm(
                    initial={
                        'total': cycle.electricity_bill_total if cycle else 0,
                        'paid': cycle.electricity_bill_paid if cycle else 0,
                    }
                ),
                'can_generate': self._can_generate(),
            }
        )
        return context

    def _can_generate(self):
        user = self.request.user
        return (
            user.is_super_manager
            or user.is_superuser
            or user.is_monthly_manager
        )


class SetHouseRentView(SuperManagerRequiredMixin, View):
    def post(self, request):
        month = request.POST.get('month', current_month_str())
        form = HouseRentForm(request.POST)
        if form.is_valid():
            try:
                set_house_rent(
                    month,
                    form.cleaned_data['total'],
                    form.cleaned_data.get('paid') or 0,
                    set_by=request.user,
                )
                messages.success(request, 'বাসা ভাড়া আপডেট হয়েছে।')
            except ValidationError as exc:
                messages.error(request, exc.messages[0])
        else:
            messages.error(request, 'Invalid house rent data.')
        return redirect(f'{reverse("bills:manage")}?month={month}')


class SetElectricityView(SuperManagerRequiredMixin, View):
    def post(self, request):
        month = request.POST.get('month', current_month_str())
        form = ElectricityForm(request.POST)
        if form.is_valid():
            try:
                set_electricity(
                    month,
                    form.cleaned_data['total'],
                    form.cleaned_data.get('paid') or 0,
                    set_by=request.user,
                )
                messages.success(request, 'বিদ্যুৎ বিল আপডেট হয়েছে।')
            except ValidationError as exc:
                messages.error(request, exc.messages[0])
        else:
            messages.error(request, 'Invalid electricity bill data.')
        return redirect(f'{reverse("bills:manage")}?month={month}')


class GenerateBillsView(ManagerRequiredMixin, View):
    def post(self, request):
        month = request.POST.get('month', current_month_str())
        try:
            generate_bills(month, generated_by=request.user)
            messages.success(request, 'মাসিক বিল জেনারেট হয়েছে।')
        except ValidationError as exc:
            messages.error(request, exc.messages[0])

        if request.user.is_super_manager or request.user.is_superuser:
            return redirect(f'{reverse("bills:manage")}?month={month}')
        return redirect(f'{reverse("bills:summary")}?month={month}')


class BillSummaryView(ManagerRequiredMixin, TemplateView):
    template_name = 'bills/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            bills = list(get_all_bills_for_month(month))
            cycle = get_cycle(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            bills = list(get_all_bills_for_month(month))
            cycle = get_cycle(month)

        context.update({'month': month, 'bills': bills, 'cycle': cycle})
        return context
