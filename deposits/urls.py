from django.urls import path

from .views import (
    ApproveDepositView,
    DepositClaimView,
    MyDepositsView,
    PendingDepositsView,
    RejectDepositView,
)

app_name = 'deposits'

urlpatterns = [
    path('', MyDepositsView.as_view(), name='my_deposits'),
    path('claim/', DepositClaimView.as_view(), name='claim'),
    path('pending/', PendingDepositsView.as_view(), name='pending'),
    path('<int:deposit_id>/approve/', ApproveDepositView.as_view(), name='approve'),
    path('<int:deposit_id>/reject/', RejectDepositView.as_view(), name='reject'),
]
