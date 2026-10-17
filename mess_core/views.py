from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView

from accounts.models import User
from .forms import MessSettingsForm, MonthlyFixedMealForm
from .models import MessSettings, MonthlyFixedMeal, MonthlyManagerAssignment
from .services.fixed_meal import set_fixed_meal
from .services.manager import assign_monthly_manager


class SuperManagerMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_super_manager or self.request.user.is_superuser

	def handle_no_permission(self):
		messages.error(self.request, 'Super Manager access required.')
		return redirect('dashboard:home')


class SettingsView(SuperManagerMixin, TemplateView):
	template_name = 'mess_core/settings.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = MessSettingsForm(instance=MessSettings.objects.first())
		return context

	def post(self, request):
		form = MessSettingsForm(request.POST, instance=MessSettings.objects.first())
		if form.is_valid():
			settings_obj = form.save(commit=False)
			settings_obj.updated_by = request.user
			settings_obj.save()
			messages.success(request, 'Settings updated.')
		else:
			messages.error(request, 'Please correct the settings form.')
		return redirect('mess_core:settings')


class ManagerAssignmentView(SuperManagerMixin, ListView):
	template_name = 'mess_core/manager.html'
	context_object_name = 'assignments'
	queryset = MonthlyManagerAssignment.objects.select_related('user', 'assigned_by').all()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['members'] = User.objects.filter(is_active_member=True).order_by('full_name')
		context['active_manager'] = MonthlyManagerAssignment.objects.filter(is_active=True).select_related('user').first()
		return context

	def post(self, request):
		try:
			assign_monthly_manager(int(request.POST['user_id']), request.POST['month'], request.user)
			messages.success(request, 'Monthly Manager assigned.')
		except (ValueError, KeyError):
			messages.error(request, 'Invalid manager assignment.')
		except Exception as exc:
			messages.error(request, str(exc))
		return redirect('mess_core:manager')


class FixedMealView(SuperManagerMixin, ListView):
	template_name = 'mess_core/fixed_meal.html'
	context_object_name = 'fixed_meals'
	queryset = MonthlyFixedMeal.objects.all()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = MonthlyFixedMealForm()
		return context

	def post(self, request):
		form = MonthlyFixedMealForm(request.POST)
		if form.is_valid():
			set_fixed_meal(
				form.cleaned_data['month'].strftime('%Y-%m'),
				form.cleaned_data['fixed_meal_count'],
				request.user,
			)
			messages.success(request, 'Fixed meal count updated.')
		else:
			messages.error(request, 'Please correct the fixed meal form.')
		return redirect('mess_core:fixed_meal')
