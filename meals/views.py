from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View

from meals.services.meal import (
    current_month_str,
    get_mess_settings,
    get_daily_meal_summary,
    get_monthly_summary,
    get_user_meals_for_month,
    is_past_cutoff,
    parse_month,
    toggle_meals,
)


class MealListView(LoginRequiredMixin, TemplateView):
    template_name = 'meals/my_meals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            meals = get_user_meals_for_month(self.request.user, month)
            start, end = parse_month(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            meals = get_user_meals_for_month(self.request.user, month)
            start, end = parse_month(month)

        settings_obj = get_mess_settings()
        context.update(
            {
                'month': month,
                'meals': meals,
                'month_start': start,
                'month_end': end,
                'today': timezone.localdate(),
                'cutoff_time': settings_obj.meal_off_cutoff_time,
                'past_cutoff': is_past_cutoff(),
                'can_view_summary': self._can_view_summary(),
            }
        )
        return context

    def _can_view_summary(self):
        user = self.request.user
        return user.is_super_manager or user.is_superuser or user.is_monthly_manager


class MealToggleView(LoginRequiredMixin, View):
    def post(self, request):
        month = request.POST.get('month', current_month_str())
        date_str = request.POST.get('date')
        meal_type = request.POST.get('meal_type')
        enabled = request.POST.get('enabled') == 'true'

        try:
            from datetime import date as date_cls

            target_date = date_cls.fromisoformat(date_str)
            existing = get_user_meals_for_month(request.user, month)
            daily = next((m for m in existing if m.date == target_date), None)
            if daily is None:
                messages.error(request, 'Invalid date.')
                return redirect(f'{reverse("meals:my_meals")}?month={month}')

            breakfast = daily.breakfast
            lunch = daily.lunch
            dinner = daily.dinner

            if meal_type == 'breakfast':
                breakfast = enabled
            elif meal_type == 'lunch':
                lunch = enabled
            elif meal_type == 'dinner':
                dinner = enabled
            else:
                messages.error(request, 'Invalid meal type.')
                return redirect(f'{reverse("meals:my_meals")}?month={month}')

            toggle_meals(request.user, target_date, breakfast, lunch, dinner)
            messages.success(request, 'Meal updated.')
        except ValidationError as exc:
            messages.error(request, exc.message)

        return redirect(f'{reverse("meals:my_meals")}?month={month}')


class MealSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'meals/summary.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            summary = get_monthly_summary(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            summary = get_monthly_summary(month)

        context.update({'month': month, 'summary': summary})
        return context


class DailyMealSummaryView(MealSummaryView):
    template_name = 'meals/daily_summary.html'

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        month = self.request.GET.get('month', current_month_str())
        try:
            daily_summary = get_daily_meal_summary(month)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
            month = current_month_str()
            daily_summary = get_daily_meal_summary(month)
        context.update({'month': month, 'daily_summary': daily_summary})
        return context
