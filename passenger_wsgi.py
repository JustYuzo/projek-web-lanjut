import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Jika passenger_wsgi.py berada di dalam folder rental_mobil_ai,
# naik satu folder agar Django tetap bisa membaca project.
if os.path.basename(CURRENT_DIR) == "rental_mobil_ai":
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
else:
    PROJECT_ROOT = CURRENT_DIR

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rental_mobil_ai.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()