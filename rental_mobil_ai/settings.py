from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ========== FUNGSI PEMBANTU ==========
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

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key-change-this-in-production")

# UPDATE: Menambahkan domain PythonAnywhere
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost", "VergonSmartDrive.pythonanywhere.com"])

# UPDATE: Menambahkan domain untuk keamanan form (CSRF)
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    ["http://127.0.0.1:8000", "http://localhost:8000", "https://VergonSmartDrive.pythonanywhere.com"]
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ========== DATABASE ==========
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ========== MEDIA (Cloudinary) ==========
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ========== STATIC FILES ==========
STATIC_URL = '/static/'
STATIC_ROOT = '/home/VergonSmartDrive/staticfiles' # Path absolut untuk PythonAnywhere

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ... (bagian INSTALLED_APPS, MIDDLEWARE, dll tetap sama dengan punya Anda) ...
# (Pastikan Anda menyalin bagian bawah kode Anda yang belum saya tulis ulang agar tidak ada yang terlewat)

# ========== KEAMANAN PRODUKSI ==========
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Disarankan False jika di PythonAnywhere sudah pakai opsi HTTPS otomatis
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False) 
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"