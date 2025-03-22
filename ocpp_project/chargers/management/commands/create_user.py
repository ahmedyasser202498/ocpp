from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class Command(BaseCommand):
    help = 'Create a superuser if one does not already exist and generate JWT token'

    def handle(self, *args, **kwargs):
        SUPERUSER_USERNAME = 'admin'
        SUPERUSER_EMAIL = 'admin@example.com'
        SUPERUSER_PASSWORD = 'admin'

        user, created = User.objects.get_or_create(
            username=SUPERUSER_USERNAME,
            defaults={
                'email': SUPERUSER_EMAIL,
                'password': SUPERUSER_PASSWORD
            }
        )

        if created:
            user.set_password(SUPERUSER_PASSWORD)
            user.is_superuser = True
            user.is_staff = True
            user.save()

            

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        print(f'Successfully created superuser with username: {SUPERUSER_USERNAME}',flush=True)
        print(f'JWT Access Token >>>>   {access_token}',flush=True)
        print(f'JWT Refresh Token >>>>   {refresh_token}',flush=True)