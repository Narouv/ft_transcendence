#!/bin/bash


python /var/django-site/manage.py migrate --noinput
python /var/django-site/manage.py collectstatic --noinput

echo "Running backend in ${PROJ_MODE} mode (change in PROJ_MODE env var)"
if [ "${PROJ_MODE}" = "prod" ]; then
	exec daphne -b 0.0.0.0 backend.asgi:application
else
	exec python manage.py runserver 0.0.0.0:8000
fi
