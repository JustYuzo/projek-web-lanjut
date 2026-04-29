from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('booking/<int:car_id>/', views.booking, name='booking'),
    path('history/', views.history, name='history'),
]