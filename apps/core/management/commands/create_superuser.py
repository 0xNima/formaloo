import os

from django.core.management import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        username = os.getenv('SUPERUSER_USERNAME')
        password = os.getenv('SUPERUSER_PASSWORD')

        if any([not username, not password]):
            self.stdout.write(self.style.ERROR(f'username or password should provided'))

        try:
            superuser = User.objects.create_superuser(username=username, password=password)
            superuser.save()

            self.stdout.write(self.style.SUCCESS('superuser created'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'failed to created superuser: {e}'))
