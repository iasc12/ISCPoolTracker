"""
Django settings for config project.
"""

import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-in-production",
)

DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "false",
).lower() == "true"


ALLOWED_HOSTS = [
    "iscpooltracker.onrender.com",
    "isac1213.pythonanywhere.com",
    "localhost",
    "127.0.0.1",
]


CSRF_TRUSTED_ORIGINS = [
    "https://iscpooltracker.onrender.com",
    "https://isac1213.pythonanywhere.com",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tracker",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {
        "BACKEND":
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


MAILERS = {
    "default": {
        "BACKEND":
            "django.core.mail.backends.smtp.EmailBackend",

        "OPTIONS": {
            "host": os.getenv(
                "EMAIL_HOST",
                "smtp.gmail.com",
            ),

            "port": int(
                os.getenv(
                    "EMAIL_PORT",
                    "587",
                )
            ),

            "username": os.getenv(
                "EMAIL_HOST_USER",
                "",
            ),

            "password": os.getenv(
                "EMAIL_HOST_PASSWORD",
                "",
            ),

            "use_tls": True,
        },
    },
}


DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "",
)


POOL_TRACKER_REMINDER_EMAIL = os.getenv(
    "POOL_TRACKER_REMINDER_EMAIL",
    "",
)


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
