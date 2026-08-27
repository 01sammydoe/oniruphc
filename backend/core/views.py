from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse


def api_root(request):
	return JsonResponse({
		'service': 'new oniru phc api',
		'health': '/api/health/',
	})


class HealthCheckView(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request):
		return Response({'status': 'ok', 'service': 'new oniru phc api'})
