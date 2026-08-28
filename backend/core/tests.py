from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from .models import Appointment, Patient, StaffProfile


class HealthCheckTests(TestCase):
	def test_api_root(self):
		response = APIClient().get('/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['health'], '/api/health/')

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
