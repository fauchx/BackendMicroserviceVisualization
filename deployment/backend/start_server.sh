#!/bin/bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd backend; python manage.py createsuperuser --no-input)
fi
#(gunicorn backend.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
#nginx -g "daemon off;"
(gunicorn home.wsgi --bind 0.0.0.0:8010 --timeout 120 --workers 1) &
nginx -g "daemon off;"
