from pathlib import Path
from django.conf import settings
from rental.models import Car

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def cari_gambar(*keywords):
    semua_gambar = []

    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
        semua_gambar.extend(MEDIA_ROOT.rglob(ext))

    for keyword in keywords:
        keyword = keyword.lower()

        for gambar in semua_gambar:
            nama_file = gambar.name.lower()

            if keyword in nama_file:
                return gambar.relative_to(MEDIA_ROOT).as_posix()

    return ""


cars = [
    {
        "name": "Toyota Calya",
        "brand": "Toyota",
        "transmission": "Matic/Manual",
        "capacity": 5,
        "price": 576000,
        "stock": 2,
        "image": cari_gambar("calya"),
    },
    {
        "name": "Toyota All New Avanza",
        "brand": "Toyota",
        "transmission": "Matic/Manual",
        "capacity": 6,
        "price": 504000,
        "stock": 2,
        "image": cari_gambar("all-new-avanza", "avanza", "avz"),
    },
    {
        "name": "Daihatsu Xenia",
        "brand": "Daihatsu",
        "transmission": "Matic/Manual",
        "capacity": 6,
        "price": 600000,
        "stock": 2,
        "image": cari_gambar("xenia"),
    },
    {
        "name": "Toyota Grand New Avanza",
        "brand": "Toyota",
        "transmission": "Matic/Manual",
        "capacity": 6,
        "price": 648000,
        "stock": 2,
        "image": cari_gambar("grand-new-avanza", "avanza"),
    },
    {
        "name": "Toyota Grand New Innova",
        "brand": "Toyota",
        "transmission": "Matic/Manual",
        "capacity": 6,
        "price": 576000,
        "stock": 1,
        "image": cari_gambar("grand-new-innova", "innova"),
    },
    {
        "name": "Toyota Innova Reborn",
        "brand": "Toyota",
        "transmission": "Matic/Manual",
        "capacity": 6,
        "price": 864000,
        "stock": 1,
        "image": cari_gambar("innova-reborn", "innova"),
    },
    {
        "name": "Toyota Fortuner",
        "brand": "Toyota",
        "transmission": "Matic/Manual",
        "capacity": 6,
        "price": 1824000,
        "stock": 1,
        "image": cari_gambar("fortuner"),
    },
    {
        "name": "Toyota Alphard",
        "brand": "Toyota",
        "transmission": "Matic",
        "capacity": 6,
        "price": 3840000,
        "stock": 1,
        "image": cari_gambar("alphard"),
    },
    {
        "name": "Isuzu Elf",
        "brand": "Isuzu",
        "transmission": "Manual",
        "capacity": 13,
        "price": 1920000,
        "stock": 1,
        "image": cari_gambar("elf", "microbus"),
    },
    {
        "name": "Toyota Hiace",
        "brand": "Toyota",
        "transmission": "Manual",
        "capacity": 13,
        "price": 1392000,
        "stock": 1,
        "image": cari_gambar("hiace"),
    },
]


print("Menghapus data mobil lama...")
Car.objects.all().delete()

print("Memasukkan data mobil baru...")

for item in cars:
    image_path = item.pop("image")

    car = Car.objects.create(
        name=item["name"],
        brand=item["brand"],
        transmission=item["transmission"],
        capacity=item["capacity"],
        price=item["price"],
        stock=item["stock"],
    )

    if image_path:
        car.image = image_path
        car.save(update_fields=["image"])
        print(f"{car.name} berhasil ditambahkan. Gambar: {image_path}")
    else:
        print(f"{car.name} berhasil ditambahkan. Gambar belum ditemukan.")

print("Selesai.")
print("Total data mobil sekarang:", Car.objects.count())