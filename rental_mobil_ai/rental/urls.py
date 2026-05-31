from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("booking/<int:car_id>/", views.booking, name="booking"),
    path("history/", views.history, name="history"),
    path("ai/", views.ai_rekomendasi, name="ai"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),
    path("api/cars/", views.api_cars, name="api_cars"),
]