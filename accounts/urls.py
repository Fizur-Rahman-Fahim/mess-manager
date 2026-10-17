from django.urls import path

from .views import (
    ApproveUserView,
    PendingApprovalView,
    PendingUsersListView,
    RegisterView,
    UserLoginView,
    UserLogoutView,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('pending/', PendingApprovalView.as_view(), name='pending_approval'),
    path('pending-users/', PendingUsersListView.as_view(), name='pending_users'),
    path('approve/<int:user_id>/', ApproveUserView.as_view(), name='approve_user'),
]
