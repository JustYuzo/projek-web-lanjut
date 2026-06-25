from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("katalog/", views.katalog, name="katalog"),
    path("detail/<int:car_id>/", views.detail_mobil, name="detail_mobil"),
    path("mobil/<int:car_id>/", views.detail_mobil, name="detail"),

    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_page, name="logout"),

    path("profil/", views.profil_user, name="profil_user"),

    path("payment/<int:car_id>/", views.payment, name="payment"),
    path("booking/<int:car_id>/", views.booking, name="booking"),
    path("payment-bank/<int:car_id>/", views.payment_bank, name="payment_bank"),
    path("payment-ewallet/<int:car_id>/", views.payment_ewallet, name="payment_ewallet"),
    path("konfirmasi-payment/<int:car_id>/<str:metode>/", views.konfirmasi_payment, name="konfirmasi_payment"),

    path("history/", views.history, name="history"),
    path("kuitansi/<int:booking_id>/", views.cetak_kuitansi_user, name="cetak_kuitansi_user"),

    path("admin-dashboard/mobil/", views.admin_mobil, name="admin_mobil"),
    path("admin-dashboard/mobil/tambah/", views.admin_tambah_mobil, name="admin_tambah_mobil"),
    path("admin-dashboard/mobil/edit/<int:car_id>/", views.admin_edit_mobil, name="admin_edit_mobil"),
    path("admin-dashboard/mobil/hapus/<int:car_id>/", views.admin_hapus_mobil, name="admin_hapus_mobil"),

    path("admin-dashboard/booking/", views.admin_booking, name="admin_booking"),
    path("admin-dashboard/booking/update-status/<int:booking_id>/", views.admin_update_status, name="admin_update_status"),
    path("admin-dashboard/booking/kuitansi/<int:booking_id>/", views.cetak_kuitansi_admin, name="cetak_kuitansi_admin"),

    path("admin-dashboard/profil-user/", views.admin_profile, name="admin_profile"),
    path("admin-dashboard/profil-user/<int:profile_id>/", views.admin_profile_detail, name="admin_profile_detail"),
    path("admin-dashboard/profil-user/<int:profile_id>/update-status/", views.admin_update_profile_status, name="admin_update_profile_status"),

    path("ai/", views.ai_rekomendasi, name="ai"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),

    path("api/cars/", views.api_cars, name="api_cars"),
]
