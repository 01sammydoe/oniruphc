import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import StaffProfile


STAFF = [
    ('doctor', 'Dr. Oniru', 'doctor'),
    ('nurse', 'Nurse Oniru', 'nurse'),
    ('frontdesk', 'Oniru Front Desk', 'front_desk'),
]


class Command(BaseCommand):
    help = 'Create the three default development staff accounts.'

    def handle(self, *args, **options):
        default_password = os.environ.get('STAFF_DEFAULT_PASSWORD', 'ChangeMe123!')
        for username, full_name, role in STAFF:
            first_name, last_name = full_name.split(' ', 1)
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first_name,
                'last_name': last_name,
            })
            if created:
                user.set_password(default_password)
                user.save(update_fields=['password'])
            StaffProfile.objects.update_or_create(user=user, defaults={'role': role})
            action = 'Created' if created else 'Verified'
            self.stdout.write(f'{action} {role} account: {username}')
        self.stdout.write(self.style.SUCCESS('Default staff accounts are ready.'))
