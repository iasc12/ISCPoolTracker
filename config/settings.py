"""
Django settings for config project.
"""

import os
from pathlib import Path

import dj_database_url


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
# HOSTS
# ============================================================

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "iscpooltracker.onrender.com",
    "isac1213.pythonanywhere.com",
]


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
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

    "tracker",
]


# ============================================================
# MIDDLEWARE
# ============================================================

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


# ============================================================
# URLS
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

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

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []


# ============================================================
# WHITENOISE
# ============================================================

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
# EMAIL
# ============================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.gmail.com",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
)

EMAIL_USE_TLS = True


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

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)