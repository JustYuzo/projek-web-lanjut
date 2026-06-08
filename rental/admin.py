from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "mobil",
        "tanggal",
        "hari",
        "total",
        "metode_pembayaran",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "metode_pembayaran",
        "tanggal",
    )

    search_fields = (
        "nama",
        "mobil",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )