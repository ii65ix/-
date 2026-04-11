import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "ينشئ سوبر أدمن للموقع الأونلاين. عرّفي في Render (Secret): "
        "DJANGO_SUPERUSER_USERNAME و DJANGO_SUPERUSER_PASSWORD"
    )

    def handle(self, *args, **options):
        User = get_user_model()

        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()

        if not username or not password:
            if getattr(settings, "DEBUG", False):
                username = username or "ALI7"
                password = password or "A1234"
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "لم يُنشأ سوبر أدمن: أضيفي في Render → Environment (Secret):\n"
                        "  DJANGO_SUPERUSER_USERNAME = اسم المستخدم\n"
                        "  DJANGO_SUPERUSER_PASSWORD = كلمة المرور\n"
                        "ثم أعيدي تشغيل الخدمة (Manual Deploy)."
                    )
                )
                return

        force_pw = os.environ.get("DJANGO_SUPERUSER_FORCE_PASSWORD", "").lower() in (
            "1",
            "true",
            "yes",
        )

        existing = User.objects.filter(username=username).first()
        if existing is None:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser [{username}] created. Open /admin/ on your site."
                )
            )
            return

        existing.is_staff = True
        existing.is_superuser = True
        if email:
            existing.email = email
        if force_pw:
            existing.set_password(password)
        existing.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser [{username}] updated (staff/superuser). "
                f"Password {'reset' if force_pw else 'unchanged; set FORCE_PASSWORD=1 to reset'}."
            )
        )
