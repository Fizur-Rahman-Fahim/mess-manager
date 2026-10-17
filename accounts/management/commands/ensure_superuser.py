import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        'Create the first Super Manager from environment variables '
        '(SUPERUSER_MOBILE, SUPERUSER_NAME, SUPERUSER_PASSWORD). Safe to run on every deploy.'
    )

    def handle(self, *args, **options):
        mobile = os.environ.get('SUPERUSER_MOBILE', '').strip()
        name = os.environ.get('SUPERUSER_NAME', '').strip() or 'Super Manager'
        password = os.environ.get('SUPERUSER_PASSWORD', '')

        if not mobile or not password:
            self.stdout.write('SUPERUSER_MOBILE / SUPERUSER_PASSWORD not set; skipping.')
            return

        User = get_user_model()
        if User.objects.filter(mobile_number=mobile).exists():
            self.stdout.write('Super Manager already exists; nothing to do.')
            return

        User.objects.create_superuser(mobile_number=mobile, password=password, full_name=name)
        self.stdout.write(self.style.SUCCESS('Super Manager created.'))
