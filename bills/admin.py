from django.contrib import admin

from .models import MonthlyBillCycle, UserBillRecord


@admin.register(MonthlyBillCycle)
class MonthlyBillCycleAdmin(admin.ModelAdmin):
    list_display = (
        'month',
        'house_rent_total',
        'electricity_bill_total',
        'meal_rate',
        'total_meal_count',
        'set_by',
        'updated_at',
    )
    date_hierarchy = 'month'


@admin.register(UserBillRecord)
class UserBillRecordAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'month',
        'total_due',
        'total_deposit',
        'balance',
        'meal_cost',
    )
    list_filter = ('month',)
    search_fields = ('user__full_name', 'user__mobile_number')
    date_hierarchy = 'month'
