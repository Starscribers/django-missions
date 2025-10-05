from __future__ import annotations

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    # SQLite is the default for simplicity
    DB_ENGINE: str = "django.db.backends.sqlite3"
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 0
    DB_NAME: str = "db.sqlite3"
    CELERY_RESULT_BACKEND: str | None = "django-db"  # Use django-db for SQLite
