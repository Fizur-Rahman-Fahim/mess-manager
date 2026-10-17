from django.contrib import admin

from .models import DailyMeal


@admin.register(DailyMeal)
class DailyMealAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'breakfast', 'lunch', 'dinner')
    list_filter = ('date', 'breakfast', 'lunch', 'dinner')
    search_fields = ('user__full_name', 'user__mobile_number')
    date_hierarchy = 'date'
