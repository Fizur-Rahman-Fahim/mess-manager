from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from config.health import healthz

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('api.urls')),
    path('meals/', include('meals.urls')),
    path('deposits/', include('deposits.urls')),
    path('expenses/', include('expenses.urls')),
    path('bills/', include('bills.urls')),
    path('complaints/', include('complaints.urls')),
    path('mess/', include('mess_core.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
