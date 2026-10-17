from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, ListView, TemplateView, View

from deposits.forms import DepositClaimForm
from deposits.models import Deposit
from deposits.services.deposit import (
    approve_deposit,
    claim_deposit,
    count_pending_deposits,
    get_pending_deposits,
    get_user_deposits,
    reject_deposit,
)
from meals.services.meal import current_month_str


class MyDepositsView(LoginRequiredMixin, TemplateView):
    template_name = 'deposits/my_deposits.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            deposits = list(get_user_deposits(self.request.user, month))
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            deposits = list(get_user_deposits(self.request.user, month))

        approved_total = sum(
            d.amount for d in deposits if d.status == Deposit.STATUS_APPROVED
        )
        context.update(
            {
                'month': month,
                'deposits': deposits,
                'approved_total': approved_total,
                'can_manage': self._can_manage(),
            }
        )
        return context

    def _can_manage(self):
        user = self.request.user
        return user.is_super_manager or user.is_superuser or user.is_monthly_manager


class DepositClaimView(LoginRequiredMixin, FormView):
    template_name = 'deposits/claim.html'
    form_class = DepositClaimForm
    success_url = reverse_lazy('deposits:my_deposits')

    def get_initial(self):
        return {'date_claimed': timezone.localdate()}

    def form_valid(self, form):
        try:
            claim_deposit(
                self.request.user,
                form.cleaned_data['amount'],
                form.cleaned_data['date_claimed'],
                form.cleaned_data.get('note', ''),
            )
            messages.success(
                self.request,
                'জমার অনুরোধ পাঠানো হয়েছে। ম্যানেজার অনুমোদনের অপেক্ষায়।',
            )
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            return self.form_invalid(form)
        return super().form_valid(form)


class PendingDepositsView(LoginRequiredMixin, ListView):
    template_name = 'deposits/pending.html'
    context_object_name = 'deposits'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (
            request.user.is_super_manager
            or request.user.is_superuser
            or request.user.is_monthly_manager
        ):
            messages.error(request, 'Monthly Manager or Super Manager access required.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_pending_deposits()


class ApproveDepositView(LoginRequiredMixin, View):
    def post(self, request, deposit_id):
        if not (
            request.user.is_super_manager
            or request.user.is_superuser
            or request.user.is_monthly_manager
        ):
            messages.error(request, 'Monthly Manager or Super Manager access required.')
            return redirect('dashboard:home')

        deposit = get_object_or_404(Deposit, pk=deposit_id, status=Deposit.STATUS_PENDING)
        try:
            approve_deposit(deposit, request.user)
            messages.success(request, f'৳{deposit.amount} জমা অনুমোদিত হয়েছে।')
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
        return redirect('deposits:pending')


class RejectDepositView(LoginRequiredMixin, View):
    def post(self, request, deposit_id):
        if not (
            request.user.is_super_manager
            or request.user.is_superuser
            or request.user.is_monthly_manager
        ):
            messages.error(request, 'Monthly Manager or Super Manager access required.')
            return redirect('dashboard:home')

        deposit = get_object_or_404(Deposit, pk=deposit_id, status=Deposit.STATUS_PENDING)
        try:
            reject_deposit(deposit, request.user)
            messages.success(request, 'জমার অনুরোধ প্রত্যাখ্যান হয়েছে।')
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
        return redirect('deposits:pending')
