from django.contrib import admin

from .models import Deposit


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date_claimed', 'status', 'approved_by', 'created_at')
    list_filter = ('status', 'date_claimed')
    search_fields = ('user__full_name', 'user__mobile_number', 'note')
    date_hierarchy = 'date_claimed'
    readonly_fields = ('created_at', 'approved_at')
