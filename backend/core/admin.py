from django.contrib import admin
from .models import Appointment, Patient, StaffProfile


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ('appointment_date', 'appointment_time', 'full_name', 'service', 'price', 'payment_status', 'paid_at', 'status', 'phone')
	list_filter = ('status', 'payment_status', 'service', 'appointment_date')
	search_fields = ('full_name', 'email', 'phone', 'patient__patient_number')
	date_hierarchy = 'appointment_date'
	list_editable = ('status',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ('patient_number', 'full_name_display', 'phone', 'sex', 'date_of_birth', 'updated_at')
	list_display_links = ('patient_number', 'full_name_display')
	search_fields = ('patient_number', 'first_name', 'last_name', 'phone', 'email')
	list_filter = ('sex', 'blood_group', 'created_at')
	date_hierarchy = 'created_at'
	readonly_fields = ('created_at', 'updated_at')
	fieldsets = (
		('Identity', {'fields': ('patient_number', 'user', 'first_name', 'middle_name', 'last_name', 'state_of_origin', 'nationality', 'date_of_birth', 'sex')}),
		('Contact', {'fields': ('phone', 'email', 'address')}),
		('Emergency contact', {'fields': ('next_of_kin', 'emergency_contact_name', 'emergency_contact_phone')}),
		('Clinical notes', {'fields': ('blood_group', 'allergies', 'medical_notes')}),
		('Record history', {'fields': ('created_at', 'updated_at')}),
	)

	@admin.display(description='Patient', ordering='last_name')
	def full_name_display(self, obj):
		return obj.full_name


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')
	list_filter = ('role',)
	search_fields = ('user__username', 'user__first_name', 'user__last_name')
