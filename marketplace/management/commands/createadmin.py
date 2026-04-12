"""
Management command to create an admin account.
Usage: python manage.py createadmin --email admin@createch.com --password Admin@1234
"""
import uuid

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from marketplace.models import AuthCredential, User


class Command(BaseCommand):
    help = 'Create an admin account (only accessible via CLI)'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--password', type=str, required=True, help='Admin password')
        parser.add_argument('--name', type=str, default='Platform Admin', help='Display name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']

        if AuthCredential.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Account with email {email} already exists.'))
            # Update role to admin
            try:
                cred = AuthCredential.objects.get(email=email)
                user = User.objects.get(firebase_uid=cred.firebase_uid)
                user.role = 'admin'
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {email} role to admin.'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR('User profile not found.'))
            return

        firebase_uid = f'admin_{uuid.uuid4().hex[:16]}'

        User.objects.create(
            firebase_uid=firebase_uid,
            email=email,
            first_name=name.split()[0],
            last_name=' '.join(name.split()[1:]),
            full_name=name,
            role='admin',
        )

        AuthCredential.objects.create(
            firebase_uid=firebase_uid,
            email=email,
            password_hash=make_password(password),
        )

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Admin account created!\n'
            f'   Email: {email}\n'
            f'   Name:  {name}\n'
            f'   UID:   {firebase_uid}\n'
            f'\n   Log in at the web app with these credentials.\n'
        ))
