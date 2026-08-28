from django.urls import path

from .views import AccountCreateView, AppointmentListCreateView, FrontDeskPatientLookupView, FrontDeskPaymentView, FrontDeskRevenueView, HealthCheckView, MyAppointmentListView, PatientLoginView, StaffLoginView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('auth/account/', AccountCreateView.as_view(), name='account-create'),
    path('auth/staff-login/', StaffLoginView.as_view(), name='staff-login'),
    path('auth/patient-login/', PatientLoginView.as_view(), name='patient-login'),
    path('appointments/', AppointmentListCreateView.as_view(), name='appointments'),
    path('appointments/mine/', MyAppointmentListView.as_view(), name='my-appointments'),
    path('appointments/mine/<int:appointment_id>/', MyAppointmentListView.as_view(), name='my-appointment-delete'),
    path('frontdesk/patient/', FrontDeskPatientLookupView.as_view(), name='frontdesk-patient'),
    path('frontdesk/appointments/<int:appointment_id>/pay/', FrontDeskPaymentView.as_view(), name='frontdesk-payment'),
    path('frontdesk/revenue/', FrontDeskRevenueView.as_view(), name='frontdesk-revenue'),
]
