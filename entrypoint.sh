#!/bin/sh
set -eu


# Ensure media path exists
mkdir -p /app/media

# Apply DB migrations (sqlite)
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear

# Start server
exec gunicorn --bind 0.0.0.0:8000 absolute_cinema.wsgi


