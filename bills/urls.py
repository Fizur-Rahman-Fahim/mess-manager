from django.urls import path

from .views import (
    BillManageView,
    BillSummaryView,
    GenerateBillsView,
    MyBillView,
    SetElectricityView,
    SetHouseRentView,
)

app_name = 'bills'

urlpatterns = [
    path('', MyBillView.as_view(), name='my_bill'),
    path('manage/', BillManageView.as_view(), name='manage'),
    path('summary/', BillSummaryView.as_view(), name='summary'),
    path('set-house-rent/', SetHouseRentView.as_view(), name='set_house_rent'),
    path('set-electricity/', SetElectricityView.as_view(), name='set_electricity'),
    path('generate/', GenerateBillsView.as_view(), name='generate'),
]
