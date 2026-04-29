from django.shortcuts import render
from datetime import date
from .models import Booking

cars = [
    {"id": 0, "name": "Toyota Avanza", "price": 350000, "capacity": "7 Orang", "transmission": "Manual", "status": "Tersedia", "image": "🚙"},
    {"id": 1, "name": "Honda Brio", "price": 300000, "capacity": "5 Orang", "transmission": "Matic", "status": "Tersedia", "image": "🚗"},
    {"id": 2, "name": "Toyota Innova", "price": 500000, "capacity": "7 Orang", "transmission": "Matic", "status": "Tersedia", "image": "🚘"},
]

def home(request):
    return render(request, "rental/home.html", {"cars": cars})

def booking(request, car_id):
    car = cars[car_id]
    error = None
    success = None

    if request.method == "POST":
        nama = request.POST.get("nama", "").strip()
        tanggal = request.POST.get("tanggal")
        hari = int(request.POST.get("hari", 1))

        total = car["price"] * hari

        if nama == "":
            error = "Nama penyewa wajib diisi."
        else:
            Booking.objects.create(
                nama=nama,
                mobil=car["name"],
                tanggal=tanggal,
                hari=hari,
                total=total
            )

            success = f"Booking berhasil! Total Rp {total:,}"

    return render(request, "rental/booking.html", {
        "car": car,
        "error": error,
        "success": success,
        "today": date.today()
    })

def history(request):
    data_booking = Booking.objects.all().order_by("-id")

    return render(request, "rental/history.html", {
        "history": data_booking
    })