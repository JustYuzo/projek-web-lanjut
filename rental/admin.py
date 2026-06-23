from django.contrib import admin
from .models import Car, Booking


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'transmission', 'capacity', 'price')
    list_filter = ('brand', 'transmission', 'capacity')
    search_fields = ('name', 'brand')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'car',
        'nama',
        'mobil',
        'tanggal',
        'hari',
        'total',
        'metode_pembayaran',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'metode_pembayaran',
        'created_at',
    )

    search_fields = (
        'nama',
        'mobil',
        'user__username',
    )

    list_editable = ('status',)