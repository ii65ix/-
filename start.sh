#!/usr/bin/env bash
# تشغيل أونلاين (Render): الترحيل → الأسئلة → السوبر أدمن → Gunicorn
set -e
export PORT="${PORT:-10000}"

echo "==> migrate"
python manage.py migrate --no-input

echo "==> seed questions (if empty)"
python manage.py seed_questions

echo "==> superuser (needs DJANGO_SUPERUSER_* on Render)"
python manage.py ensure_admin_ali7

echo "==> gunicorn on 0.0.0.0:${PORT}"
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}"
