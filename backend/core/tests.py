from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from .models import Appointment, DoctorConsultation, NurseVitals, Patient, StaffProfile


class HealthCheckTests(TestCase):
	def test_api_root(self):
		response = APIClient().get('/')

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], '/admin/')

	def test_health_check(self):
		response = APIClient().get('/api/health/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['status'], 'ok')


class PatientModelTests(TestCase):
	def test_patient_full_name_and_ordering(self):
		patient = Patient.objects.create(
			patient_number='PHC-0001',
			first_name='Ada',
			last_name='Okafor',
			phone='08000000000',
		)

		self.assertEqual(patient.full_name, 'Ada Okafor')
		self.assertEqual(str(patient), 'Ada Okafor (PHC-0001)')


class AppointmentApiTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='patient', password='Password123!')
		self.patient = Patient.objects.create(patient_number='PHC-0002', user=self.user, first_name='Test', last_name='Patient', phone='08000000000', email='patient@example.com')

	def test_booking_requires_authentication(self):
		response = APIClient().post('/api/appointments/', {}, format='json')

		self.assertEqual(response.status_code, 401)

	def test_authenticated_patient_can_book(self):
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')
		response = client.post('/api/appointments/', {
			'full_name': 'Test Patient', 'email': 'patient@example.com', 'phone': '08000000000',
			'service': 'General consultation', 'appointment_date': '2026-10-01', 'appointment_time': '09:30',
		}, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Appointment.objects.get().patient, self.patient)

	def test_patient_cannot_book_two_active_appointments(self):
		Appointment.objects.create(
			patient=self.patient, full_name='Test Patient', email='patient@example.com', phone='08000000000',
			service='General consultation', appointment_date='2026-10-01', appointment_time='09:30',
		)
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')
		response = client.post('/api/appointments/', {
			'full_name': 'Test Patient', 'email': 'patient@example.com', 'phone': '08000000000',
			'service': 'Follow-up visit', 'appointment_date': '2026-10-02', 'appointment_time': '09:30',
		}, format='json')

		self.assertEqual(response.status_code, 409)

	def test_due_appointment_is_removed_from_patient_list(self):
		Appointment.objects.create(
			patient=self.patient, full_name='Test Patient', email='patient@example.com', phone='08000000000',
			service='General consultation', appointment_date='2020-01-01', appointment_time='09:30',
		)
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')

		response = client.get('/api/appointments/mine/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), [])
		self.assertFalse(Appointment.objects.exists())

	def test_patient_can_delete_own_appointment(self):
		appointment = Appointment.objects.create(
			patient=self.patient, full_name='Test Patient', email='patient@example.com', phone='08000000000',
			service='General consultation', appointment_date='2026-10-01', appointment_time='09:30',
		)
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')

		response = client.delete(f'/api/appointments/mine/{appointment.id}/')

		self.assertEqual(response.status_code, 204)
		self.assertFalse(Appointment.objects.exists())

	def test_different_patients_can_each_book_an_appointment(self):
		second_user = User.objects.create_user(username='patient-two', password='Password123!')
		second_patient = Patient.objects.create(patient_number='PHC-0003', user=second_user, first_name='Second', last_name='Patient', phone='08000000001', email='second@example.com')
		first_client = APIClient()
		first_client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')
		second_client = APIClient()
		second_client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=second_user).key}')

		for client, patient, date in ((first_client, self.patient, '2026-10-01'), (second_client, second_patient, '2026-10-02')):
			response = client.post('/api/appointments/', {
				'full_name': patient.full_name, 'email': patient.email, 'phone': patient.phone,
				'service': 'General consultation', 'appointment_date': date, 'appointment_time': '09:30',
			}, format='json')
			self.assertEqual(response.status_code, 201)

		self.assertEqual(Appointment.objects.filter(patient__in=[self.patient, second_patient]).count(), 2)

	def test_past_appointment_is_rejected(self):
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')
		response = client.post('/api/appointments/', {
			'full_name': 'Wrong Name', 'email': 'wrong@example.com', 'phone': '000',
			'service': 'General consultation', 'appointment_date': '2020-01-01', 'appointment_time': '09:30',
		}, format='json')

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Appointment.objects.count(), 0)


class FrontDeskApiTests(TestCase):
	def setUp(self):
		self.staff = User.objects.create_user(username='frontdesk', password='Password123!', first_name='Front', last_name='Desk')
		StaffProfile.objects.create(user=self.staff, role=StaffProfile.Role.FRONT_DESK)
		self.patient = Patient.objects.create(patient_number='PHC-0100', first_name='Ada', last_name='Okafor', phone='08000000000', email='ada@example.com')
		self.appointment = Appointment.objects.create(patient=self.patient, full_name='Ada Okafor', email='ada@example.com', phone='08000000000', service='General consultation', appointment_date='2026-10-01', appointment_time='09:30')
		self.client = APIClient()
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.staff).key}')

	def test_frontdesk_can_lookup_patient_and_price(self):
		response = self.client.get('/api/frontdesk/patient/?patient_number=PHC-0100')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['appointments'][0]['price'], '5000.00')

	def test_frontdesk_can_record_payment(self):
		response = self.client.post(f'/api/frontdesk/appointments/{self.appointment.id}/pay/')

		self.assertEqual(response.status_code, 200)
		self.appointment.refresh_from_db()
		self.assertEqual(self.appointment.payment_status, Appointment.PaymentStatus.PAID)
		self.assertIsNotNone(self.appointment.paid_at)

	def test_revenue_uses_payment_date_not_appointment_date(self):
		self.appointment.payment_status = Appointment.PaymentStatus.PAID
		self.appointment.paid_at = timezone.now()
		self.appointment.save(update_fields=['payment_status', 'paid_at'])
		response = self.client.get(f"/api/frontdesk/revenue/?date={timezone.localdate().isoformat()}")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['total'], '5000')

	def test_non_frontdesk_cannot_use_frontdesk_api(self):
		patient_client = APIClient()
		patient_user = User.objects.create_user(username='patient-two', password='Password123!')
		patient_client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=patient_user).key}')

		self.assertEqual(patient_client.get('/api/frontdesk/revenue/').status_code, 403)


class NurseVitalsApiTests(TestCase):
	def setUp(self):
		self.nurse = User.objects.create_user(username='nurse', password='Password123!', first_name='Nurse', last_name='Care')
		StaffProfile.objects.create(user=self.nurse, role=StaffProfile.Role.NURSE)
		self.patient = Patient.objects.create(patient_number='PHC-0200', first_name='Ayo', last_name='Bello', phone='08000000000', email='ayo@example.com')
		self.client = APIClient()
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.nurse).key}')

	def test_nurse_can_save_vitals(self):
		response = self.client.post('/api/nurse/patient-vitals/', {
			'patient_number': 'PHC-0200', 'temperature': '36.8', 'pulse_rate': '72',
			'blood_pressure': '120/80', 'weight': '68.5', 'height': '172',
			'recent_test_result': 'Normal', 'diagnosis': 'Routine review',
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(NurseVitals.objects.get(patient=self.patient).diagnosis, 'Routine review')

	def test_patient_profile_includes_nurse_vitals(self):
		NurseVitals.objects.create(patient=self.patient, temperature='37.0', recorded_by=self.nurse)
		patient_user = User.objects.create_user(username='patient-vitals', password='Password123!')
		self.patient.user = patient_user
		self.patient.save(update_fields=['user'])
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=patient_user).key}')

		response = client.get('/api/profile/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['vitals']['temperature'], '37.0')


class DoctorConsultationApiTests(TestCase):
	def setUp(self):
		self.doctor = User.objects.create_user(username='doctor', password='Password123!', first_name='Dr.', last_name='Care')
		StaffProfile.objects.create(user=self.doctor, role=StaffProfile.Role.DOCTOR)
		self.patient = Patient.objects.create(patient_number='PHC-0300', first_name='Grace', last_name='Adebayo', phone='08000000000', email='grace@example.com')
		self.client = APIClient()
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.doctor).key}')

	def test_doctor_can_load_patient_profile_and_record_diagnosis_and_drugs(self):
		response = self.client.post('/api/doctor/patient-record/', {
			'patient_number': 'PHC-0300',
			'diagnosis': 'Upper respiratory infection',
			'medical_notes': 'Patient reports cough and fever for two days.',
			'drugs': 'Amoxicillin 500mg, Paracetamol 500mg',
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['patient']['name'], 'Grace Adebayo')
		self.assertEqual(response.json()['consultation']['diagnosis'], 'Upper respiratory infection')
		self.assertEqual(DoctorConsultation.objects.get(patient=self.patient).drugs, 'Amoxicillin 500mg, Paracetamol 500mg')

	def test_doctor_daily_summary_counts_patients_attended(self):
		DoctorConsultation.objects.create(
			patient=self.patient,
			diagnosis='Malaria',
			drugs='Artesunate',
			recorded_by=self.doctor,
		)

		response = self.client.get(f"/api/doctor/summary/?date={timezone.localdate().isoformat()}")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['count'], 1)
		self.assertEqual(response.json()['patients'][0]['name'], 'Grace Adebayo')


class AdminCreatedPatientLoginTests(TestCase):
	def test_admin_created_user_gets_patient_profile_on_login(self):
		user = User.objects.create_user(username='admin-created', password='Password123!', email='admin@example.com')

		response = APIClient().post('/api/auth/patient-login/', {
			'username': user.username, 'password': 'Password123!',
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['profile']['patient_number'], f'PHC-{user.pk:04d}')
		self.assertTrue(Patient.objects.filter(user=user).exists())
