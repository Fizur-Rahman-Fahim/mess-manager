from django.urls import path

from api.bill_views import (
    GenerateBillsAPIView,
    MyBillAPIView,
    SetElectricityAPIView,
    SetHouseRentAPIView,
)
from api.complaint_views import (
    AllComplaintsAPIView,
    ComplaintCreateAPIView,
    ComplaintStatusAPIView,
    MyComplaintsAPIView,
)
from api.expense_views import BazarExpenseAPIView
from api.fixed_meal_views import FixedMealAPIView
from api.deposit_views import (
    ApproveDepositAPIView,
    DepositClaimAPIView,
    MyDepositsAPIView,
    PendingDepositsAPIView,
    RejectDepositAPIView,
)
from api.meal_views import DailyMealSummaryAPIView, MealSummaryAPIView, MealToggleAPIView, MyMealsAPIView
from api.manager_views import ManagerAssignmentAPIView
from api.settings_views import SettingsAPIView
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    ApproveUserAPIView,
    LoginAPIView,
    MeAPIView,
    PendingApprovalAPIView,
    RegisterAPIView,
)

app_name = 'api'

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', MeAPIView.as_view(), name='me'),
    path('users/pending-approval/', PendingApprovalAPIView.as_view(), name='pending_approval'),
    path('users/<int:user_id>/approve/', ApproveUserAPIView.as_view(), name='approve_user'),
    path('meals/my-meals/', MyMealsAPIView.as_view(), name='my_meals'),
    path('meals/toggle/', MealToggleAPIView.as_view(), name='meal_toggle'),
    path('meals/summary/', MealSummaryAPIView.as_view(), name='meal_summary'),
    path('meals/daily-summary/', DailyMealSummaryAPIView.as_view(), name='daily_meal_summary'),
    path('meals/fixed/', FixedMealAPIView.as_view(), name='fixed_meals'),
    path('deposits/claim/', DepositClaimAPIView.as_view(), name='deposit_claim'),
    path('deposits/my-deposits/', MyDepositsAPIView.as_view(), name='my_deposits'),
    path('deposits/pending/', PendingDepositsAPIView.as_view(), name='pending_deposits'),
    path('deposits/<int:deposit_id>/approve/', ApproveDepositAPIView.as_view(), name='deposit_approve'),
    path('deposits/<int:deposit_id>/reject/', RejectDepositAPIView.as_view(), name='deposit_reject'),
    path('expenses/bazar/', BazarExpenseAPIView.as_view(), name='bazar_expenses'),
    path('bills/my-bill/', MyBillAPIView.as_view(), name='my_bill'),
    path('bills/set-house-rent/', SetHouseRentAPIView.as_view(), name='set_house_rent'),
    path('bills/set-electricity/', SetElectricityAPIView.as_view(), name='set_electricity'),
    path('bills/generate/', GenerateBillsAPIView.as_view(), name='generate_bills'),
    path('settings/', SettingsAPIView.as_view(), name='settings'),
    path('manager/assign/', ManagerAssignmentAPIView.as_view(), name='manager_assign'),
    path('complaints/', ComplaintCreateAPIView.as_view(), name='complaint_create'),
    path('complaints/my-complaints/', MyComplaintsAPIView.as_view(), name='my_complaints'),
    path('complaints/all/', AllComplaintsAPIView.as_view(), name='all_complaints'),
    path('complaints/<int:complaint_id>/status/', ComplaintStatusAPIView.as_view(), name='complaint_status'),
]
