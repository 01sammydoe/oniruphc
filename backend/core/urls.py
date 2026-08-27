from django.urls import path

from .views import AccountCreateView, HealthCheckView, StaffLoginView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('auth/account/', AccountCreateView.as_view(), name='account-create'),
    path('auth/staff-login/', StaffLoginView.as_view(), name='staff-login'),
]
