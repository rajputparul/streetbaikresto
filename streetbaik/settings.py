import os
from pathlib import Path

import cloudinary
import dj_database_url
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


# Security
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-streetbaik-change-me",
)

DEBUG = os.getenv("DEBUG", "1") == "1"

if not DEBUG and SECRET_KEY == "django-insecure-streetbaik-change-me":
    raise RuntimeError(
        "Set DJANGO_SECRET_KEY before running with DEBUG=0."
    )


ALLOWED_HOSTS = [
    h
    for h in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if h
]


# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cafe",
]


# Middleware
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


ROOT_URLCONF = "streetbaik.urls"


# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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


WSGI_APPLICATION = "streetbaik.wsgi.application"


# Database
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "data" / "streetbaik.sqlite3",
        }
    }


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Security settings
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

SECURE_SSL_REDIRECT = (
    os.getenv("SECURE_SSL_REDIRECT", "0") == "1"
)

SECURE_HSTS_SECONDS = int(
    os.getenv("SECURE_HSTS_SECONDS", "0")
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "0") == "1"
)

SECURE_HSTS_PRELOAD = (
    os.getenv("SECURE_HSTS_PRELOAD", "0") == "1"
)

CSRF_TRUSTED_ORIGINS = [
    o
    for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if o
]


# Cafe information
CAFE_NAME = "Street Baik Resto Cafe"
CAFE_PHONE = "8129935964"
CAFE_EMAIL = "streetbaikresto@gmail.com"

CAFE_ADDRESS = (
    "Railway Station Rd, near Aluva Junction, "
    "Periyar Nagar, Aluva, Kochi, Kerala 683101"
)

CAFE_INSTAGRAM = "https://www.instagram.com/streetbaik"
CAFE_MAPS = "https://maps.app.goo.gl/4Z3DfaMugVHmci488"


# WhatsApp / Twilio
TWILIO_ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID",
    "",
)

TWILIO_AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN",
    "",
)

TWILIO_WHATSAPP_FROM = os.getenv(
    "TWILIO_WHATSAPP_FROM",
    "",
)

CLIENT_WHATSAPP = os.getenv(
    "CLIENT_WHATSAPP",
    "8129935964",
)


# Delivery
DELIVERY_RADIUS_KM = int(
    os.getenv("DELIVERY_RADIUS_KM", "4")
)


# Website
SITE_URL = os.getenv(
    "SITE_URL",
    "",
)