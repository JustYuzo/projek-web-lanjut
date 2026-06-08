from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("katalog/", views.katalog, name="katalog"),
    path("detail/<int:car_id>/", views.detail_mobil, name="detail_mobil"),
    path("payment/<int:car_id>/", views.payment, name="payment"),
    path("payment-bank/<int:car_id>/", views.payment_bank, name="payment_bank"),
    path("booking/<int:car_id>/", views.booking, name="booking"),
    path("history/", views.history, name="history"),
    path("ai/", views.ai_rekomendasi, name="ai"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),
    path("api/cars/", views.api_cars, name="api_cars"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_page, name="logout"),
    path("payment-ewallet/<int:car_id>/", views.payment_ewallet, name="payment_ewallet"),
]