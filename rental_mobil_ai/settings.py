from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# =====================
# BASE DIRECTORY
# =====================
BASE_DIR = Path(__file__).resolve().parent.parent


# =====================
# HELPER ENV
# =====================
def env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in ["1", "true", "yes", "on"]


def env_list(name, default=None):
    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default or []

    return [item.strip() for item in value.split(",") if item.strip()]


# =====================
# SECRET KEY & DEBUG
# =====================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-key-smartdrive-local-only"
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    [
        "127.0.0.1",
        "localhost",
    ]
)

# Untuk hosting nanti, isi di .env:
# ALLOWED_HOSTS=namadomain.com,www.namadomain.com,127.0.0.1,localhost


# =====================
# CSRF TRUSTED ORIGINS
# =====================
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
)

# Untuk hosting nanti, isi di .env:
# CSRF_TRUSTED_ORIGINS=https://namadomain.com,https://www.namadomain.com


# =====================
# API KEY
# =====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# =====================
# INSTALLED APPS
# =====================
INSTALLED_APPS = [
    # Django bawaan
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Wajib untuk django-allauth
    "django.contrib.sites",

    # App project
    "rental",

    # Django Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    # Provider Google
    "allauth.socialaccount.providers.google",
]


# =====================
# MIDDLEWARE
# =====================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise untuk static file saat hosting.
    # Aktif kalau kamu install whitenoise.
    # Jika belum install, boleh comment baris ini dulu.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Wajib untuk django-allauth
    "allauth.account.middleware.AccountMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "rental_mobil_ai.urls"


# =====================
# TEMPLATE SETTING
# =====================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

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


WSGI_APPLICATION = "rental_mobil_ai.wsgi.application"


# =====================
# DATABASE
# =====================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Untuk hosting serius nanti lebih aman pakai PostgreSQL.
# SQLite masih boleh untuk development/local.


# =====================
# PASSWORD VALIDATION
# =====================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =====================
# INTERNATIONAL
# =====================
LANGUAGE_CODE = "id-id"

TIME_ZONE = "Asia/Jakarta"

USE_I18N = True

USE_TZ = True


# =====================
# STATIC FILES
# =====================
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# =====================
# MEDIA FILES
# =====================
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =====================
# DEFAULT PK
# =====================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =====================
# LOGIN & LOGOUT
# =====================
LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/login/"


# =====================
# DJANGO ALLAUTH SETTING
# =====================
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Login biasa Django
    "django.contrib.auth.backends.ModelBackend",

    # Login Google dari django-allauth
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Tidak perlu verifikasi email untuk development.
# Untuk production serius, nanti boleh diganti menjadi "mandatory".
ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_UNIQUE_EMAIL = True

# Setting baru django-allauth:
# login menggunakan email dan tidak memaksa input username lagi.
ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_SIGNUP_FIELDS = ["email*"]

# Biar user yang sudah login tidak bisa buka halaman login/signup allauth lagi.
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True

# Supaya login Google otomatis membuat akun tanpa halaman daftar tambahan.
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_LOGIN_ON_GET = True

# Jika email Google sama dengan akun lokal yang sudah ada,
# akun Google akan otomatis terhubung ke user tersebut.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "EMAIL_AUTHENTICATION": True,
    }
}


# =====================
# SECURITY UNTUK HOSTING
# =====================
if not DEBUG:
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True