from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

USERNAME = "ALI7"
PASSWORD = "A1234"


class Command(BaseCommand):
    help = "Create or update superuser ALI7 (change password in production)."

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=USERNAME,
            defaults={
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.is_staff = True
        user.is_superuser = True
        user.set_password(PASSWORD)
        user.save()
        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"User {USERNAME} {action}. Log in at /admin/"))
