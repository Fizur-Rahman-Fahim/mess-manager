from django.contrib import admin

from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
	list_display = ('title', 'raised_by', 'status', 'handled_by', 'created_at', 'resolved_at')
	list_filter = ('status', 'created_at')
