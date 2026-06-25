from django.contrib import admin
from .models import Car, Booking, Profile


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "brand",
        "transmission",
        "capacity",
        "price",
        "stock",
        "status_stok_display",
    )

    list_filter = (
        "brand",
        "transmission",
        "capacity",
        "stock",
    )

    search_fields = (
        "name",
        "brand",
        "transmission",
    )

    list_editable = (
        "stock",
    )

    fieldsets = (
        ("Data Mobil", {
            "fields": (
                "name",
                "brand",
                "transmission",
                "capacity",
                "price",
                "stock",
                "image",
            )
        }),
    )

    def status_stok_display(self, obj):
        if obj.stock > 0:
            return f"Tersedia {obj.stock} Unit"
        return "Stok Habis"

    status_stok_display.short_description = "Status Stok"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "car",
        "nama",
        "mobil",
        "tanggal",
        "hari",
        "total",
        "kode_unik",
        "total_bayar",
        "metode_pembayaran",
        "bank_pembayaran",
        "status",
        "stock_dikurangi",
        "created_at",
    )

    list_filter = (
        "status",
        "metode_pembayaran",
        "bank_pembayaran",
        "stock_dikurangi",
        "created_at",
    )

    search_fields = (
        "nama",
        "mobil",
        "user__username",
        "user__email",
        "car__name",
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "kode_unik",
        "total_bayar",
        "stock_dikurangi",
    )

    fieldsets = (
        ("Data User dan Mobil", {
            "fields": (
                "user",
                "car",
                "nama",
                "mobil",
            )
        }),

        ("Data Sewa", {
            "fields": (
                "tanggal",
                "hari",
                "total",
            )
        }),

        ("Data Pembayaran", {
            "fields": (
                "metode_pembayaran",
                "bank_pembayaran",
                "bukti_transfer",
                "kode_unik",
                "total_bayar",
            )
        }),

        ("Status Booking", {
            "fields": (
                "status",
                "stock_dikurangi",
            )
        }),

        ("Waktu Sistem", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "nama_lengkap",
        "no_hp",
        "nik_ktp",
        "nomor_sim_a",
        "status_verifikasi",
        "data_lengkap_display",
        "tanggal_verifikasi",
        "diperbarui_pada",
    )

    list_filter = (
        "status_verifikasi",
        "jenis_kelamin",
        "provinsi",
        "kota",
    )

    search_fields = (
        "user__username",
        "user__email",
        "nama_lengkap",
        "no_hp",
        "nik_ktp",
        "nomor_sim_a",
        "kota",
        "provinsi",
    )

    readonly_fields = (
        "dibuat_pada",
        "diperbarui_pada",
        "tanggal_verifikasi",
    )

    fieldsets = (
        ("Akun User", {
            "fields": (
                "user",
                "foto_profil",
            )
        }),

        ("Biodata Pribadi", {
            "fields": (
                "nama_lengkap",
                "no_hp",
                "tempat_lahir",
                "tanggal_lahir",
                "jenis_kelamin",
                "nik_ktp",
                "foto_ktp",
            )
        }),

        ("Data SIM A", {
            "fields": (
                "nomor_sim_a",
                "masa_berlaku_sim",
                "foto_sim_a",
            )
        }),

        ("Alamat Lengkap", {
            "fields": (
                "alamat_lengkap",
                "kota",
                "provinsi",
                "kode_pos",
            )
        }),

        ("Kontak Darurat", {
            "fields": (
                "kontak_darurat_nama",
                "kontak_darurat_no_hp",
                "kontak_darurat_hubungan",
            )
        }),

        ("Verifikasi Admin", {
            "fields": (
                "status_verifikasi",
                "catatan_admin",
                "diverifikasi_oleh",
                "tanggal_verifikasi",
            )
        }),

        ("Waktu Sistem", {
            "fields": (
                "dibuat_pada",
                "diperbarui_pada",
            )
        }),
    )

    def data_lengkap_display(self, obj):
        if obj.data_lengkap():
            return "Lengkap"
        return "Belum Lengkap"

    data_lengkap_display.short_description = "Data Profil"
