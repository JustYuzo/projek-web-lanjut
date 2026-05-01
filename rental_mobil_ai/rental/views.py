from django.shortcuts import render
from django.http import JsonResponse
from datetime import date
from .models import Booking

cars = [
    {
        "id": 0,
        "name": "Toyota Avanza",
        "price": 350000,
        "capacity": "7 Orang",
        "transmission": "Manual",
        "status": "Tersedia",
        "image": "🚙",
    },
    {
        "id": 1,
        "name": "Honda Brio",
        "price": 300000,
        "capacity": "5 Orang",
        "transmission": "Matic",
        "status": "Tersedia",
        "image": "🚗",
    },
    {
        "id": 2,
        "name": "Toyota Innova",
        "price": 500000,
        "capacity": "7 Orang",
        "transmission": "Matic",
        "status": "Tersedia",
        "image": "🚘",
    },
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
    return render(request, "rental/history.html", {"history": data_booking})


def ai_rekomendasi(request):
    hasil = []
    pesan = None

    if request.method == "POST":
        jumlah_orang = int(request.POST.get("jumlah_orang", 1))
        budget = int(request.POST.get("budget", 100000))
        kebutuhan = request.POST.get("kebutuhan")

        for car in cars:
            kapasitas = int(car["capacity"].split()[0])

            if kapasitas >= jumlah_orang and car["price"] <= budget:
                if kebutuhan == "Hemat" and car["price"] <= 350000:
                    hasil.append(car)
                elif kebutuhan == "Keluarga" and kapasitas >= 7:
                    hasil.append(car)
                elif kebutuhan == "Nyaman":
                    hasil.append(car)

        if not hasil:
            pesan = "Tidak ada mobil yang sesuai dengan kebutuhan kamu."

    return render(request, "rental/ai.html", {
        "hasil": hasil,
        "pesan": pesan
    })


def api_cars(request):
    return JsonResponse({
        "status": "success",
        "message": "Data mobil berhasil diambil",
        "data": cars
    })