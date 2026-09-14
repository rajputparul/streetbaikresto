from pathlib import Path
import os
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.getenv("DJANGO_SECRET_KEY","django-insecure-streetbaik-change-me")
DEBUG=os.getenv("DEBUG","1") == "1"
ALLOWED_HOSTS=[h for h in os.getenv("ALLOWED_HOSTS","127.0.0.1,localhost").split(",") if h]
INSTALLED_APPS=["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","cafe"]
MIDDLEWARE=["django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF="streetbaik.urls"
TEMPLATES=[{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION="streetbaik.wsgi.application"
DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"data"/"streetbaik.sqlite3"}}
LANGUAGE_CODE="en-us"
TIME_ZONE="Asia/Kolkata"
USE_I18N=True
USE_TZ=True
STATIC_URL="/static/"
STATICFILES_DIRS=[BASE_DIR/"static"]
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

CAFE_NAME="Street Baik Resto Cafe"
CAFE_PHONE="8129935964"
CAFE_EMAIL="streetbaikresto@gmail.com"
CAFE_ADDRESS="Railway Station Rd, near Aluva Junction, Periyar Nagar, Aluva, Kochi, Kerala 683101"
CAFE_INSTAGRAM="https://www.instagram.com/streetbaik"
CAFE_MAPS="https://maps.app.goo.gl/4Z3DfaMugVHmci488"
TWILIO_ACCOUNT_SID=os.getenv("TWILIO_ACCOUNT_SID","")
TWILIO_AUTH_TOKEN=os.getenv("TWILIO_AUTH_TOKEN","")
TWILIO_WHATSAPP_FROM=os.getenv("TWILIO_WHATSAPP_FROM","")
CLIENT_WHATSAPP=os.getenv("CLIENT_WHATSAPP","8129935964")
