from django.urls import path

from .views import FixedMealView, ManagerAssignmentView, SettingsView

app_name = 'mess_core'

urlpatterns = [
    path('settings/', SettingsView.as_view(), name='settings'),
    path('manager/', ManagerAssignmentView.as_view(), name='manager'),
    path('fixed-meals/', FixedMealView.as_view(), name='fixed_meal'),
]