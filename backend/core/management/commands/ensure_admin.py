import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	help = 'Create or update the configured Django admin account.'

	def handle(self, *args, **options):
		username = os.environ.get('DJANGO_ADMIN_USERNAME', '').strip()
		email = os.environ.get('DJANGO_ADMIN_EMAIL', '').strip()
		password = os.environ.get('DJANGO_ADMIN_PASSWORD', '')

		if not username or not password:
			self.stdout.write('Django admin credentials are not configured; skipping.')
			return

		user_model = get_user_model()
		user, created = user_model.objects.get_or_create(
			username=username,
			defaults={'email': email},
		)
		user.email = email
		user.is_staff = True
		user.is_superuser = True
		user.set_password(password)
		user.save()
		action = 'Created' if created else 'Updated'
		self.stdout.write(self.style.SUCCESS(f'{action} Django admin account: {username}'))