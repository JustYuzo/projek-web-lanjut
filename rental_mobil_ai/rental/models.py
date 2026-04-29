from django.db import models

class Booking(models.Model):
    nama = models.CharField(max_length=100)
    mobil = models.CharField(max_length=100)
    tanggal = models.DateField()
    hari = models.IntegerField()
    total = models.IntegerField()

    def __str__(self):
        return f"{self.nama} - {self.mobil}"