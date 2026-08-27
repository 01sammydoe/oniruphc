from django.test import TestCase
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
	def test_api_root(self):
		response = APIClient().get('/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['health'], '/api/health/')

	def test_health_check(self):
		response = APIClient().get('/api/health/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['status'], 'ok')
