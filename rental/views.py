from django.shortcuts import render
from django.http import JsonResponse
from datetime import date
from .models import Booking

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt


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


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def home(request):
    return render(request, "rental/home.html", {"cars": cars})

def login_page(request):
    return render(request, "rental/login.html")


def signup_page(request):
    return render(request, "rental/signup.html")


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


@csrf_exempt
def ai_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if user_message.strip() == "":
                return JsonResponse({
                    "reply": "Pesan tidak boleh kosong."
                })

            daftar_mobil = ""
            for car in cars:
                daftar_mobil += (
                    f"- {car['name']}, harga Rp {car['price']:,}/hari, "
                    f"kapasitas {car['capacity']}, transmisi {car['transmission']}, "
                    f"status {car['status']}\n"
                )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
Kamu adalah asisten AI untuk website rental mobil.
Jawab dengan bahasa Indonesia yang ramah, singkat, dan mudah dipahami.
Bantu pelanggan memilih mobil berdasarkan jumlah orang, budget, kebutuhan, dan kenyamanan.

Data mobil yang tersedia:
{daftar_mobil}
"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                stream=False
            )

            jawaban = response.choices[0].message.content

            return JsonResponse({
                "reply": jawaban
            })

        except Exception as e:
            return JsonResponse({
                "reply": "Terjadi error: " + str(e)
            })

    return JsonResponse({
        "reply": "Method tidak diizinkan."
    })