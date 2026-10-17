from django.contrib import admin

from .models import BazarExpense


@admin.register(BazarExpense)
class BazarExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'bazar_type', 'amount', 'added_by', 'month', 'created_at')
    list_filter = ('bazar_type', 'month')
    search_fields = ('description', 'added_by__full_name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'month')
