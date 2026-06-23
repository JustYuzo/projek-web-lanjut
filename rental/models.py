from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from rembg import remove
from io import BytesIO
from django.core.files.base import ContentFile
import os


class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    transmission = models.CharField(max_length=50)
    capacity = models.IntegerField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='cars/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            image_path = self.image.path

            try:
                with open(image_path, 'rb') as input_file:
                    input_data = input_file.read()

                output_data = remove(input_data)

                img = Image.open(BytesIO(output_data)).convert("RGBA")

                buffer = BytesIO()
                img.save(buffer, format="PNG")

                file_name = os.path.splitext(os.path.basename(self.image.name))[0]
                new_file_name = f"{file_name}_removebg.png"

                self.image.save(
                    f"cars/{new_file_name}",
                    ContentFile(buffer.getvalue()),
                    save=False
                )

                super().save(update_fields=["image"])

            except Exception as e:
                print("Gagal remove background:", e)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu Konfirmasi'),
        ('diproses', 'Sedang Diproses'),
        ('selesai', 'Berhasil'),
        ('ditolak', 'Ditolak'),
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

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='menunggu'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama} - {self.mobil} - {self.status}"