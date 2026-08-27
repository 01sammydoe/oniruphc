from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

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


class AccountCreateView(APIView):
	def post(self, request):
		username = request.data.get('username', '').strip()
		password = request.data.get('password', '')
		first_name = request.data.get('first_name', '').strip()
		last_name = request.data.get('last_name', '').strip()
		if not username or not password or not first_name:
			return Response({'detail': 'First name, username, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
		if User.objects.filter(username=username).exists():
			return Response({'detail': 'That username is already in use.'}, status=status.HTTP_409_CONFLICT)
		user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
		token, _ = Token.objects.get_or_create(user=user)
		return Response({'token': token.key, 'user': {'name': user.get_full_name(), 'role': 'patient'}}, status=status.HTTP_201_CREATED)


class StaffLoginView(APIView):
	def post(self, request):
		user = authenticate(username=request.data.get('username', ''), password=request.data.get('password', ''))
		if user is None or not hasattr(user, 'staff_profile'):
			return Response({'detail': 'Invalid staff credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
		token, _ = Token.objects.get_or_create(user=user)
		profile = user.staff_profile
		return Response({'token': token.key, 'user': {'name': user.get_full_name(), 'role': profile.role}})
