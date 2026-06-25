from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL untuk login Google dari django-allauth
    path('accounts/', include('allauth.urls')),

    # URL utama aplikasi rental
    path('', include('rental.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)