#!/usr/bin/env bash
set -o errexit
# البناء فقط — الترحيل والسوبر يوزر في start.sh عند التشغيل
python manage.py collectstatic --no-input
