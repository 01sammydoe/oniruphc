from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date, parse_time
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment, Patient

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
		middle_name = request.data.get('middle_name', '').strip()
		state_of_origin = request.data.get('state_of_origin', '').strip()
		nationality = request.data.get('nationality', 'Nigerian').strip()
		email = request.data.get('email', '').strip()
		phone = request.data.get('phone', '').strip()
		blood_group = request.data.get('blood_group', '').strip()
		next_of_kin = request.data.get('next_of_kin', '').strip()
		date_of_birth = request.data.get('date_of_birth') or None
		address = request.data.get('address', '').strip()
		if not username or not password or not first_name or not last_name or not phone or not email:
			return Response({'detail': 'Surname, first name, email, phone, username, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
		if User.objects.filter(username=username).exists():
			return Response({'detail': 'That username is already in use.'}, status=status.HTTP_409_CONFLICT)
		user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
		patient = Patient.objects.create(
			patient_number=f'PHC-{user.pk:04d}', user=user, first_name=first_name, middle_name=middle_name,
			last_name=last_name, state_of_origin=state_of_origin, nationality=nationality, email=email,
			phone=phone, blood_group=blood_group, next_of_kin=next_of_kin, date_of_birth=date_of_birth,
			address=address,
		)
		token, _ = Token.objects.get_or_create(user=user)
		return Response({'token': token.key, 'user': {'name': patient.full_name, 'role': 'patient'}, 'profile': {
			'patient_number': patient.patient_number, 'surname': patient.last_name, 'middle_name': patient.middle_name,
			'first_name': patient.first_name, 'state_of_origin': patient.state_of_origin, 'nationality': patient.nationality,
			'email': patient.email, 'phone': patient.phone, 'blood_group': patient.blood_group, 'next_of_kin': patient.next_of_kin,
			'date_of_birth': patient.date_of_birth, 'address': patient.address,
		}}, status=status.HTTP_201_CREATED)


class StaffLoginView(APIView):
	def post(self, request):
		user = authenticate(username=request.data.get('username', ''), password=request.data.get('password', ''))
		if user is None or not hasattr(user, 'staff_profile'):
			return Response({'detail': 'Invalid staff credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
		token, _ = Token.objects.get_or_create(user=user)
		profile = user.staff_profile
		return Response({'token': token.key, 'user': {'name': user.get_full_name(), 'role': profile.role}})


class PatientLoginView(APIView):
	def post(self, request):
		user = authenticate(username=request.data.get('username', ''), password=request.data.get('password', ''))
		if user is None or not hasattr(user, 'patient_record'):
			return Response({'detail': 'Invalid patient credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
		token, _ = Token.objects.get_or_create(user=user)
		patient = user.patient_record
		return Response({'token': token.key, 'user': {'name': patient.full_name, 'role': 'patient'}, 'profile': {
			'patient_number': patient.patient_number, 'surname': patient.last_name, 'middle_name': patient.middle_name,
			'first_name': patient.first_name, 'state_of_origin': patient.state_of_origin, 'nationality': patient.nationality,
			'email': patient.email, 'phone': patient.phone, 'blood_group': patient.blood_group, 'next_of_kin': patient.next_of_kin,
			'date_of_birth': patient.date_of_birth, 'address': patient.address,
		}})


class AppointmentListCreateView(APIView):
	def get_permissions(self):
		return [AllowAny()] if self.request.method == 'GET' else [IsAuthenticated()]

	def get(self, request):
		appointments = Appointment.objects.filter(status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED])[:6]
		return Response([{
			'date': appointment.appointment_date.isoformat(), 'time': appointment.appointment_time.strftime('%H:%M'),
			'service': appointment.service, 'status': appointment.get_status_display(),
		} for appointment in appointments])

	def post(self, request):
		if not hasattr(request.user, 'patient_record'):
			return Response({'detail': 'Only signed-in patients can book appointments.'}, status=status.HTTP_403_FORBIDDEN)
		if Appointment.objects.filter(patient=request.user.patient_record, status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]).exists():
			return Response({'detail': 'You already have an active appointment. It must be completed or cancelled before booking another.'}, status=status.HTTP_409_CONFLICT)
		required = ('full_name', 'email', 'phone', 'service', 'appointment_date', 'appointment_time')
		if any(not request.data.get(field) for field in required):
			return Response({'detail': 'Please complete all required appointment fields.'}, status=status.HTTP_400_BAD_REQUEST)
		appointment_date = parse_date(request.data['appointment_date'])
		appointment_time = parse_time(request.data['appointment_time'])
		if not appointment_date or not appointment_time:
			return Response({'detail': 'Please provide a valid date and time.'}, status=status.HTTP_400_BAD_REQUEST)
		appointment_datetime = timezone.make_aware(datetime.combine(appointment_date, appointment_time), timezone.get_current_timezone())
		if appointment_datetime <= timezone.now():
			return Response({'detail': 'Please choose a future appointment date and time.'}, status=status.HTTP_400_BAD_REQUEST)
		if request.data['service'] not in Appointment.SERVICE_PRICES:
			return Response({'detail': 'Please select a valid clinic service.'}, status=status.HTTP_400_BAD_REQUEST)
		appointment = Appointment.objects.create(
			patient=request.user.patient_record,
			full_name=request.user.patient_record.full_name, email=request.user.patient_record.email, phone=request.user.patient_record.phone,
			service=request.data['service'], price=Appointment.SERVICE_PRICES.get(request.data['service'], 0), appointment_date=appointment_date, appointment_time=appointment_time,
			notes=request.data.get('notes', '').strip(),
		)
		return Response({'id': appointment.id, 'message': 'Appointment request received.', 'appointment': {
			'id': appointment.id, 'date': appointment.appointment_date.isoformat(), 'time': appointment.appointment_time.strftime('%H:%M'), 'service': appointment.service,
			'price': str(appointment.price), 'status': appointment.status, 'status_label': appointment.get_status_display(),
		}}, status=status.HTTP_201_CREATED)


class MyAppointmentListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		if not hasattr(request.user, 'patient_record'):
			return Response({'detail': 'Only patients have appointments.'}, status=status.HTTP_403_FORBIDDEN)
		appointments = request.user.patient_record.appointments.all()
		now = timezone.localtime()
		for appointment in appointments:
			if timezone.make_aware(datetime.combine(appointment.appointment_date, appointment.appointment_time), timezone.get_current_timezone()) <= now:
				appointment.delete()
		appointments = request.user.patient_record.appointments.all()
		return Response([{
			'id': appointment.id, 'date': appointment.appointment_date.isoformat(),
			'time': appointment.appointment_time.strftime('%H:%M'), 'service': appointment.service,
			'status': appointment.status, 'status_label': appointment.get_status_display(),
		} for appointment in appointments])

	def delete(self, request, appointment_id):
		if not hasattr(request.user, 'patient_record'):
			return Response({'detail': 'Only patients can delete appointments.'}, status=status.HTTP_403_FORBIDDEN)
		try:
			appointment = request.user.patient_record.appointments.get(id=appointment_id)
		except Appointment.DoesNotExist:
			return Response({'detail': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
		appointment.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class IsFrontDesk(BasePermission):
	message = 'Front desk access is required.'

	def has_permission(self, request, view):
		return hasattr(request.user, 'staff_profile') and request.user.staff_profile.role == 'front_desk'


class FrontDeskOnlyView(APIView):
	permission_classes = [IsAuthenticated, IsFrontDesk]


class FrontDeskPatientLookupView(FrontDeskOnlyView):
	def get(self, request):
		patient_number = request.query_params.get('patient_number', '').strip()
		if not patient_number:
			return Response({'detail': 'Enter a patient number.'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			patient = Patient.objects.get(patient_number__iexact=patient_number)
		except Patient.DoesNotExist:
			return Response({'detail': 'No patient was found with that patient number.'}, status=status.HTTP_404_NOT_FOUND)
		appointments = patient.appointments.all()
		return Response({'patient': {'patient_number': patient.patient_number, 'name': patient.full_name, 'phone': patient.phone}, 'appointments': [{
			'id': appointment.id, 'service': appointment.service, 'date': appointment.appointment_date.isoformat(),
			'time': appointment.appointment_time.strftime('%H:%M'), 'status': appointment.get_status_display(),
			'price': str(appointment.price), 'payment_status': appointment.get_payment_status_display(),
		} for appointment in appointments]})


class FrontDeskPaymentView(FrontDeskOnlyView):
	def post(self, request, appointment_id):
		try:
			appointment = Appointment.objects.get(id=appointment_id)
		except Appointment.DoesNotExist:
			return Response({'detail': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
		appointment.payment_status = Appointment.PaymentStatus.PAID
		appointment.paid_at = timezone.now()
		appointment.save(update_fields=['payment_status', 'paid_at'])
		return Response({'message': 'Payment recorded.', 'amount': str(appointment.price)})


class FrontDeskRevenueView(FrontDeskOnlyView):
	def get(self, request):
		selected_date = parse_date(request.query_params.get('date', '')) or timezone.localdate()
		paid = Appointment.objects.filter(paid_at__date=selected_date, payment_status=Appointment.PaymentStatus.PAID)
		by_service = paid.values('service').annotate(total=Sum('price')).order_by('service')
		return Response({'date': selected_date.isoformat(), 'total': str(paid.aggregate(total=Sum('price'))['total'] or 0), 'by_service': [
			{'service': item['service'], 'total': str(item['total'])} for item in by_service
		]})
