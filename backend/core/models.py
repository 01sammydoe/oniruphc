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
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(blank=True, null=True)
	sex = models.CharField(max_length=20, choices=Sex.choices, blank=True)
	phone = models.CharField(max_length=30)
	email = models.EmailField(blank=True)
	address = models.TextField(blank=True)
	emergency_contact_name = models.CharField(max_length=200, blank=True)
	emergency_contact_phone = models.CharField(max_length=30, blank=True)
	blood_group = models.CharField(max_length=5, blank=True)
	allergies = models.TextField(blank=True)
	medical_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['last_name', 'first_name']

	@property
	def full_name(self):
		return f'{self.first_name} {self.last_name}'

	def __str__(self):
		return f'{self.full_name} ({self.patient_number})'
