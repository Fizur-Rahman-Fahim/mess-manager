from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, TemplateView, View
from django_ratelimit.decorators import ratelimit

from .forms import MobileAuthenticationForm, UserRegistrationForm
from .services.member import approve_member, get_pending_members


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')
    success_message = _('Registration submitted. Please wait for Super Manager approval before logging in.')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = MobileAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser and not user.is_super_manager and not user.is_active_member:
            messages.error(
                self.request,
                _('Your account is pending approval. Please contact the Super Manager.'),
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


class PendingApprovalView(TemplateView):
    template_name = 'accounts/pending_approval.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_active_member or request.user.is_super_manager or request.user.is_superuser:
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)


class PendingUsersListView(ListView):
    template_name = 'accounts/pending_users.html'
    context_object_name = 'pending_users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_super_manager:
            messages.error(request, _('Only Super Manager can access this page.'))
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_pending_members()


class ApproveUserView(View):
    def post(self, request, user_id):
        if not request.user.is_super_manager:
            messages.error(request, _('Only Super Manager can approve members.'))
            return redirect('dashboard:home')

        user = get_object_or_404(get_pending_members(), pk=user_id)
        approve_member(user, approved_by=request.user)
        messages.success(request, _('%(name)s has been approved.') % {'name': user.full_name})
        return redirect('accounts:pending_users')
