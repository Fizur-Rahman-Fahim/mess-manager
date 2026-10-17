from django.contrib import admin

from .models import MessSettings, MonthlyFixedMeal, MonthlyManagerAssignment


@admin.register(MessSettings)
class MessSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'seat_bill_default',
        'current_bill_default',
        'breakfast_meal_value',
        'lunch_meal_value',
        'dinner_meal_value',
        'meal_off_cutoff_time',
        'updated_at',
    )


@admin.register(MonthlyManagerAssignment)
class MonthlyManagerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'is_active', 'start_date', 'end_date', 'assigned_by')
    list_filter = ('is_active', 'month')


@admin.register(MonthlyFixedMeal)
class MonthlyFixedMealAdmin(admin.ModelAdmin):
    list_display = ('month', 'fixed_meal_count', 'set_by', 'updated_at')
