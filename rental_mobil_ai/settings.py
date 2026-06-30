from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ========== FUNGSI PEMBANTU (tetap pakai punya Anda) ==========
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

# ========== KEAMANAN ==========
DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-dev-key-smartdrive-local-only"
    else:
        raise RuntimeError("SECRET_KEY belum diisi. Tambahkan SECRET_KEY di file .env atau environment variable Render.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    ["http://127.0.0.1:8000", "http://localhost:8000"]
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ========== PERUBAHAN 1: FOLDER PERSISTEN UNTUK RENDER ==========
# Buat folder 'persistent' di root proyek (akan di-mount oleh Render)
PERSISTENT_DIR = BASE_DIR / 'persistent'

# ========== PERUBAHAN 2: DATABASE SQLITE DI DALAM PERSISTENT ==========
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": PERSISTENT_DIR / "db.sqlite3",  # <-- Pindah ke persistent
    }
}

# ========== PERUBAHAN 3: MEDIA (FOTO MOBIL) DI DALAM PERSISTENT ==========
MEDIA_URL = "/media/"
MEDIA_ROOT = PERSISTENT_DIR / "media"  # <-- Pindah ke persistent

# ========== STATIC FILES (tetap di BASE_DIR, aman) ==========
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ========== APLIKASI (tidak berubah) ==========
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "rental",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <-- WhiteNoise sudah benar
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rental_mobil_ai.urls"

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

WSGI_APPLICATION = "rental_mobil_ai.wsgi.application"

# ========== VALIDASI PASSWORD (tidak berubah) ==========
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========== INTERNASIONALISASI ==========
LANGUAGE_CODE = "id-id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========== LOGIN ==========
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# ========== ALLAUTH (tidak berubah) ==========
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*"]
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "EMAIL_AUTHENTICATION": True,
    }
}

# ========== PERUBAHAN 4: KONFIGURASI KEAMANAN PRODUKSI (DI RENDER) ==========
if not DEBUG:
    # Render sudah menyediakan HTTPS, jadi kita aktifkan
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

    # Redirect HTTP ke HTTPS (ini penting)
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)

    # Cookie hanya dikirim lewat HTTPS
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)

    # Keamanan tambahan
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # HSTS (bisa diaktifkan perlahan)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)