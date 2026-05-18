#!/bin/sh
set -eu


# Ensure media path exists
mkdir -p /app/media

# Apply DB migrations (sqlite)
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear

# Start server
exec daphne -b 0.0.0.0 -p 8000 absolute_cinema.asgi:application