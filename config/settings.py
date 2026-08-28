
"""
Django settings for config project.

ISC Pool Tracker
Production configuration for Render
"""

import os
from pathlib import Path

import dj_database_url


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-in-production",
)

DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "false",
).lower() == "true"


# ============================================================
# ALLOWED HOSTS
# ============================================================

ALLOWED_HOSTS = [
    "iscpooltracker.onrender.com",
    "isac1213.pythonanywhere.com",
    "localhost",
    "127.0.0.1",
]


# ============================================================
# CSRF TRUSTED ORIGINS
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    "https://iscpooltracker.onrender.com",
    "https://isac1213.pythonanywhere.com",
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # ISC Pool Tracker
    "tracker",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # IMPORTANT:
    # WhiteNoise serves Django static files in production.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

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


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator",
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

# Browser URL for static files
STATIC_URL = "/static/"


# Folder containing collected production static files
STATIC_ROOT = BASE_DIR / "staticfiles"


# No additional project-level static directory is required
# because tracker/static/ is automatically discovered.
STATICFILES_DIRS = []


# ============================================================
# WHITENOISE
# ============================================================

# WhiteNoise serves the collected files from STATIC_ROOT.
#
# This is what allows Render/Gunicorn to serve:
#
# /static/tracker/manifest.json
# /static/tracker/icon.png
# /static/tracker/icons/icon-192.png
# /static/tracker/icons/icon-512.png
# /static/tracker/sw.js

STORAGES = {
    "default": {
        "BACKEND":
            "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {
        "BACKEND":
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

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


# ============================================================
# EMAIL ADDRESSES
# ============================================================

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "",
)


POOL_TRACKER_REMINDER_EMAIL = os.getenv(
    "POOL_TRACKER_REMINDER_EMAIL",
    "",
)


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"