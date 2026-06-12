from django.db import models
from django.contrib.auth.models import User


class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    transmission = models.CharField(max_length=50)
    capacity = models.IntegerField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='cars/', blank=True, null=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu Konfirmasi'),
        ('disetujui', 'Pembayaran Disetujui'),
        ('ditolak', 'Pembayaran Ditolak'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nama = models.CharField(max_length=100)
    mobil = models.CharField(max_length=100)
    tanggal = models.DateField()
    hari = models.IntegerField()
    total = models.IntegerField()

    metode_pembayaran = models.CharField(max_length=50, blank=True, null=True)
    bank_pembayaran = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='menunggu'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama} - {self.mobil} - {self.status}"