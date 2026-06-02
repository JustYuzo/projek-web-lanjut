from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("katalog/", views.katalog, name="katalog"),
    path("booking/<int:car_id>/", views.booking, name="booking"),
    path("ai/", views.ai_rekomendasi, name="ai"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),
    path("history/", views.history, name="history"),
    path("api/cars/", views.api_cars, name="api_cars"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_page, name="logout"),
]