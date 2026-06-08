from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # arahkan ke app rental
    path('', include('rental.urls')),
    
]