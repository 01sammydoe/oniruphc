from django.contrib import admin
from .models import Appointment, NurseVitals, Patient, StaffProfile


@admin.register(NurseVitals)
class NurseVitalsAdmin(admin.ModelAdmin):
	list_display = ('patient', 'temperature', 'pulse_rate', 'blood_pressure', 'weight', 'height', 'updated_at')
	search_fields = ('patient__patient_number', 'patient__first_name', 'patient__last_name', 'diagnosis')
	readonly_fields = ('updated_at',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ('appointment_date', 'appointment_time', 'full_name', 'service', 'status', 'phone')
	list_filter = ('status', 'service', 'appointment_date')
	search_fields = ('full_name', 'email', 'phone', 'patient__patient_number')
	date_hierarchy = 'appointment_date'
	list_editable = ('status',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ('patient_number', 'phone', 'sex', 'date_of_birth')
	list_display_links = ('patient_number',)
	search_fields = ('patient_number', 'first_name', 'last_name', 'phone', 'email')
	list_filter = ('sex',)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')
	list_filter = ('role',)
	search_fields = ('user__username', 'user__first_name', 'user__last_name')
