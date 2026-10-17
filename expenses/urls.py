from django.urls import path

from .views import BazarAddView, BazarListView

app_name = 'expenses'

urlpatterns = [
    path('bazar/', BazarListView.as_view(), name='bazar_list'),
    path('bazar/add/', BazarAddView.as_view(), name='bazar_add'),
]
