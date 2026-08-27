from django.test import TestCase
from rest_framework.test import APIClient

from .models import Patient


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
