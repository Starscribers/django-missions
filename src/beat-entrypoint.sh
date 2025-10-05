#!/bin/sh
uv run python -m celery -A marktech beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
exec "$@"
