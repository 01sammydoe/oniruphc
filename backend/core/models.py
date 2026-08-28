from django.db import models
from django.contrib.auth.models import User


class StaffProfile(models.Model):
	class Role(models.TextChoices):
		DOCTOR = 'doctor', 'Doctor'
		NURSE = 'nurse', 'Nurse'
		FRONT_DESK = 'front_desk', 'Front desk'

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
	role = models.CharField(max_length=20, choices=Role.choices)

	def __str__(self):
		return f'{self.user.get_full_name()} ({self.get_role_display()})'


class Patient(models.Model):
	class Sex(models.TextChoices):
		FEMALE = 'female', 'Female'
		MALE = 'male', 'Male'
		OTHER = 'other', 'Other'
		UNDISCLOSED = 'undisclosed', 'Prefer not to say'

	patient_number = models.CharField(max_length=20, unique=True, help_text='Clinic identifier, for example PHC-0001.')
	user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='patient_record', blank=True, null=True)
	first_name = models.CharField(max_length=100)
	middle_name = models.CharField(max_length=100, blank=True)
	last_name = models.CharField(max_length=100)
	state_of_origin = models.CharField(max_length=100, blank=True)
	nationality = models.CharField(max_length=100, default='Nigerian')
	date_of_birth = models.DateField(blank=True, null=True)
	sex = models.CharField(max_length=20, choices=Sex.choices, blank=True)
	phone = models.CharField(max_length=30)
	email = models.EmailField(blank=True)
	address = models.TextField(blank=True)
	emergency_contact_name = models.CharField(max_length=200, blank=True)
	emergency_contact_phone = models.CharField(max_length=30, blank=True)
	next_of_kin = models.CharField(max_length=200, blank=True)
	blood_group = models.CharField(max_length=5, blank=True)
	allergies = models.TextField(blank=True)
	medical_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['last_name', 'first_name']

	@property
	def full_name(self):
		return ' '.join(part for part in (self.first_name, self.middle_name, self.last_name) if part)

	def __str__(self):
		return f'{self.full_name} ({self.patient_number})'


class Appointment(models.Model):
	SERVICE_PRICES = {
		'General consultation': 5000,
		'Antenatal care': 50000,
		'Immunization (0-5 years)': 0,
		'Family planning': 15000,
		'Lab/test result': 10000,
	}

	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending confirmation'
		CONFIRMED = 'confirmed', 'Confirmed'
		COMPLETED = 'completed', 'Completed'
		CANCELLED = 'cancelled', 'Cancelled'

	class PaymentStatus(models.TextChoices):
		UNPAID = 'unpaid', 'Unpaid'
		PAID = 'paid', 'Paid'

	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, related_name='appointments', blank=True, null=True)
	full_name = models.CharField(max_length=200)
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	service = models.CharField(max_length=100)
	appointment_date = models.DateField()
	appointment_time = models.TimeField()
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	price = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
	payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
	paid_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['appointment_date', 'appointment_time']

	def __str__(self):
		return f'{self.full_name} - {self.appointment_date} at {self.appointment_time}'
