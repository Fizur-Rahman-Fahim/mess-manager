from django.urls import path

from .views import AllComplaintsView, ComplaintCreateView, ComplaintStatusView, MyComplaintsView

app_name = 'complaints'

urlpatterns = [
    path('', MyComplaintsView.as_view(), name='my_complaints'),
    path('new/', ComplaintCreateView.as_view(), name='create'),
    path('all/', AllComplaintsView.as_view(), name='all'),
    path('<int:complaint_id>/status/', ComplaintStatusView.as_view(), name='status'),
]
