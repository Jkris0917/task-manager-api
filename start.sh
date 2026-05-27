#!/bin/bash
echo "Running migrations..."
python manage.py migrate
echo "Starting gunicorn..."
exec gunicorn config.wsgi --workers 1 --bind 0.0.0.0:8000 --timeout 120 --log-file -