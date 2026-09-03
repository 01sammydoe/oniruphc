from django.urls import path

from .views import AccountCreateView, AppointmentListCreateView, DoctorPatientRecordView, DoctorSummaryView, FrontDeskPatientLookupView, FrontDeskPaymentView, FrontDeskRevenueView, HealthCheckView, MyAppointmentListView, NursePatientVitalsView, PatientLoginView, PatientProfileView, StaffLoginView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('auth/account/', AccountCreateView.as_view(), name='account-create'),
    path('auth/staff-login/', StaffLoginView.as_view(), name='staff-login'),
    path('auth/patient-login/', PatientLoginView.as_view(), name='patient-login'),
    path('profile/', PatientProfileView.as_view(), name='patient-profile'),
    path('appointments/', AppointmentListCreateView.as_view(), name='appointments'),
    path('appointments/mine/', MyAppointmentListView.as_view(), name='my-appointments'),
    path('appointments/mine/<int:appointment_id>/', MyAppointmentListView.as_view(), name='my-appointment-delete'),
    path('frontdesk/patient/', FrontDeskPatientLookupView.as_view(), name='frontdesk-patient'),
    path('frontdesk/appointments/<int:appointment_id>/pay/', FrontDeskPaymentView.as_view(), name='frontdesk-payment'),
    path('frontdesk/revenue/', FrontDeskRevenueView.as_view(), name='frontdesk-revenue'),
    path('nurse/patient-vitals/', NursePatientVitalsView.as_view(), name='nurse-patient-vitals'),
    path('doctor/patient-record/', DoctorPatientRecordView.as_view(), name='doctor-patient-record'),
    path('doctor/summary/', DoctorSummaryView.as_view(), name='doctor-summary'),
]
