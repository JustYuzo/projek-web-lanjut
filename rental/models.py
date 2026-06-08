from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = [
        ("menunggu", "Menunggu Konfirmasi"),
        ("disetujui", "Disetujui"),
        ("ditolak", "Ditolak"),
    ]

    METODE_CHOICES = [
        ("bank", "Transfer Bank"),
        ("ewallet", "E-Wallet"),
    ]

    nama = models.CharField(max_length=100)
    mobil = models.CharField(max_length=100)
    tanggal = models.DateField()
    hari = models.IntegerField()
    total = models.IntegerField()

    metode_pembayaran = models.CharField(
        max_length=20,
        choices=METODE_CHOICES,
        default="bank"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="menunggu"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama} - {self.mobil} - {self.status}"