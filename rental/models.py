from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

import random

# Definisi Global untuk Status AI
AI_STATUS_CHOICES = [
    ("pending", "Belum Diperiksa"),
    ("jelas", "Jelas"),
    ("buram", "Buram"),
    ("tidak_valid", "Tidak Valid"),
]

class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    transmission = models.CharField(max_length=50)
    capacity = models.IntegerField()
    price = models.IntegerField()
    stock = models.PositiveIntegerField(
        default=1,
        help_text="Jumlah unit mobil yang tersedia untuk disewa."
    )
    image = models.ImageField(upload_to="cars/", blank=True, null=True)

    @property
    def tersedia(self):
        return self.stock > 0

    @property
    def status_stok(self):
        if self.stock > 0:
            return f"Tersedia {self.stock} Unit"
        return "Stok Habis"

    def kurangi_stock(self):
        updated = Car.objects.filter(pk=self.pk, stock__gt=0).update(stock=F("stock") - 1)
        if updated:
            self.refresh_from_db(fields=["stock"])
            return True
        return False

    def tambah_stock(self):
        Car.objects.filter(pk=self.pk).update(stock=F("stock") + 1)
        self.refresh_from_db(fields=["stock"])
        return True

    def __str__(self):
        return self.name


class Profile(models.Model):
    STATUS_BELUM_LENGKAP = "belum_lengkap"
    STATUS_MENUNGGU = "menunggu"
    STATUS_TERVERIFIKASI = "terverifikasi"
    STATUS_DITOLAK = "ditolak"

    STATUS_CHOICES = [
        (STATUS_BELUM_LENGKAP, "Belum Lengkap"),
        (STATUS_MENUNGGU, "Menunggu Verifikasi"),
        (STATUS_TERVERIFIKASI, "Terverifikasi"),
        (STATUS_DITOLAK, "Ditolak"),
    ]

    JENIS_KELAMIN_CHOICES = [("L", "Laki-laki"), ("P", "Perempuan")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    foto_profil = models.ImageField(upload_to="profile/foto/", blank=True, null=True)
    nama_lengkap = models.CharField(max_length=150, blank=True)
    no_hp = models.CharField(max_length=20, blank=True, validators=[RegexValidator(regex=r"^[0-9+\-\s]{10,20}$", message="Nomor HP harus berisi angka dan minimal 10 digit.")])
    tempat_lahir = models.CharField(max_length=100, blank=True)
    tanggal_lahir = models.DateField(blank=True, null=True)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, blank=True)
    nik_ktp = models.CharField(max_length=16, blank=True, null=True, unique=True, validators=[RegexValidator(regex=r"^[0-9]{16}$", message="NIK/KTP harus 16 digit angka.")])
    foto_ktp = models.ImageField(upload_to="profile/ktp/", blank=True, null=True)
    nomor_sim_a = models.CharField(max_length=30, blank=True)
    masa_berlaku_sim = models.DateField(blank=True, null=True)
    foto_sim_a = models.ImageField(upload_to="profile/sim/", blank=True, null=True)
    alamat_lengkap = models.TextField(blank=True)
    kota = models.CharField(max_length=100, blank=True)
    provinsi = models.CharField(max_length=100, blank=True)
    kode_pos = models.CharField(max_length=10, blank=True)
    kontak_darurat_nama = models.CharField(max_length=150, blank=True)
    kontak_darurat_no_hp = models.CharField(max_length=20, blank=True, validators=[RegexValidator(regex=r"^[0-9+\-\s]{10,20}$", message="Nomor kontak darurat harus berisi angka dan minimal 10 digit.")])
    kontak_darurat_hubungan = models.CharField(max_length=100, blank=True, help_text="Contoh: Orang tua, saudara, pasangan, teman.")
    
    # Field AI untuk Profile
    ai_status_ktp = models.CharField(max_length=20, choices=AI_STATUS_CHOICES, default="pending")
    ai_catatan_ktp = models.TextField(blank=True, null=True)
    ai_status_sim = models.CharField(max_length=20, choices=AI_STATUS_CHOICES, default="pending")
    ai_catatan_sim = models.TextField(blank=True, null=True)

    status_verifikasi = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BELUM_LENGKAP)
    catatan_admin = models.TextField(blank=True)
    diverifikasi_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="profile_diverifikasi")
    tanggal_verifikasi = models.DateTimeField(blank=True, null=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil User"
        verbose_name_plural = "Profil User"

    def __str__(self):
        return f"Profil {self.user.username}"

    def data_lengkap(self):
        wajib = [self.nama_lengkap, self.no_hp, self.tempat_lahir, self.tanggal_lahir, self.jenis_kelamin, self.nik_ktp, self.foto_ktp, self.nomor_sim_a, self.masa_berlaku_sim, self.foto_sim_a, self.alamat_lengkap, self.kota, self.provinsi, self.kode_pos, self.kontak_darurat_nama, self.kontak_darurat_no_hp, self.kontak_darurat_hubungan]
        return all(wajib)

    def bisa_booking(self):
        return self.status_verifikasi == self.STATUS_TERVERIFIKASI

    def sim_masih_berlaku(self):
        if not self.masa_berlaku_sim:
            return False
        return self.masa_berlaku_sim >= timezone.now().date()


class Booking(models.Model):
    STATUS_CHOICES = [
        ("menunggu", "Menunggu Konfirmasi"),
        ("diproses", "Sedang Diproses"),
        ("selesai", "Berhasil"),
        ("ditolak", "Ditolak"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)
    nama = models.CharField(max_length=100)
    mobil = models.CharField(max_length=100)
    tanggal = models.DateField()
    hari = models.IntegerField()
    total = models.IntegerField()
    metode_pembayaran = models.CharField(max_length=50, blank=True, null=True)
    bank_pembayaran = models.CharField(max_length=50, blank=True, null=True)
    bukti_transfer = models.ImageField(upload_to="bukti_transfer/", blank=True, null=True)
    kode_unik = models.IntegerField(default=0, help_text="Kode unik 3 angka.")
    total_bayar = models.IntegerField(default=0, help_text="Total harga sewa + kode unik.")
    
    # Field AI untuk Booking
    ai_nominal_terdeteksi = models.IntegerField(default=0, blank=True, null=True)
    ai_status_pembayaran = models.CharField(max_length=20, choices=AI_STATUS_CHOICES, default="pending")
    ai_catatan_pembayaran = models.TextField(blank=True, null=True)
    ai_raw_response = models.TextField(blank=True, null=True, help_text="Respon mentah AI.")

    stock_dikurangi = models.BooleanField(default=False, help_text="Menandai apakah stok mobil sudah dikurangi.")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="menunggu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_kode_unik(self):
        return random.randint(100, 999)

    def save(self, *args, **kwargs):
        if not self.kode_unik:
            self.kode_unik = self.generate_kode_unik()
        self.total_bayar = int(self.total) + int(self.kode_unik)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama} - {self.mobil} - {self.status}"


@receiver(post_save, sender=User)
def buat_profile_otomatis(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)