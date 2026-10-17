from django.urls import path

from .views import DailyMealSummaryView, MealListView, MealSummaryView, MealToggleView

app_name = 'meals'

urlpatterns = [
    path('', MealListView.as_view(), name='my_meals'),
    path('toggle/', MealToggleView.as_view(), name='toggle'),
    path('summary/', MealSummaryView.as_view(), name='summary'),
    path('daily-summary/', DailyMealSummaryView.as_view(), name='daily_summary'),
]
