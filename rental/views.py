from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import date
from .models import Booking

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

import os
import json
from dotenv import load_dotenv
from google import genai
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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def home(request):
    return render(request, "rental/home.html", {
        "cars": cars
    })


def katalog(request):
    return render(request, "rental/katalog.html", {
        "cars": cars
    })


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if email == "" or password == "":
            error = "Email dan kata sandi wajib diisi."
        else:
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = email

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)

                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)

                return redirect("home")
            else:
                error = "Email atau kata sandi salah."

    return render(request, "rental/login.html", {
        "error": error
    })


def signup_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    error = None

    if request.method == "POST":
        nama_depan = request.POST.get("nama_depan", "").strip()
        nama_belakang = request.POST.get("nama_belakang", "").strip()
        email = request.POST.get("email", "").strip()
        no_telpon = request.POST.get("no_telpon", "").strip()
        password = request.POST.get("password", "")
        setuju = request.POST.get("setuju")

        if nama_depan == "" or nama_belakang == "" or email == "" or no_telpon == "" or password == "":
            error = "Semua data wajib diisi."
        elif setuju is None:
            error = "Kamu harus menyetujui syarat dan ketentuan."
        elif User.objects.filter(email=email).exists():
            error = "Email sudah terdaftar."
        else:
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nama_depan,
                last_name=nama_belakang
            )

            return redirect("login")

    return render(request, "rental/signup.html", {
        "error": error
    })


def logout_page(request):
    auth_logout(request)
    return redirect("login")


def detail_mobil(request, car_id):
    if car_id < 0 or car_id >= len(cars):
        return redirect("katalog")

    car = cars[car_id]

    return render(request, "rental/detail.html", {
        "car": car
    })


@login_required(login_url="login")
def payment(request, car_id):
    if car_id < 0 or car_id >= len(cars):
        return redirect("katalog")

    car = cars[car_id]

    return render(request, "rental/payment.html", {
        "car": car,
        "today": date.today()
    })


@login_required(login_url="login")
def payment_bank(request, car_id):
    if car_id < 0 or car_id >= len(cars):
        return redirect("katalog")

    car = cars[car_id]

    return render(request, "rental/payment_bank.html", {
        "car": car,
        "today": date.today()
    })


@login_required(login_url="login")
def payment_ewallet(request, car_id):
    if car_id < 0 or car_id >= len(cars):
        return redirect("katalog")

    car = cars[car_id]

    return render(request, "rental/payment_ewallet.html", {
        "car": car,
        "today": date.today()
    })


@login_required(login_url="login")
def konfirmasi_payment(request, car_id, metode):
    if car_id < 0 or car_id >= len(cars):
        return redirect("katalog")

    car = cars[car_id]

    if request.method == "POST":
        nama = request.POST.get("nama", "").strip()
        tanggal = request.POST.get("tanggal")
        hari = request.POST.get("hari", 1)

        if nama == "":
            nama = request.user.get_full_name() or request.user.username

        if not tanggal:
            tanggal = date.today()

        try:
            hari = int(hari)
        except:
            hari = 1

        total = car["price"] * hari

        try:
            Booking.objects.create(
                nama=nama,
                mobil=car["name"],
                tanggal=tanggal,
                hari=hari,
                total=total,
                metode_pembayaran=metode,
                status="menunggu"
            )
        except TypeError:
            Booking.objects.create(
                nama=nama,
                mobil=car["name"],
                tanggal=tanggal,
                hari=hari,
                total=total
            )

        return redirect("history")

    return redirect("payment", car_id=car_id)


@login_required(login_url="login")
def booking(request, car_id):
    if car_id < 0 or car_id >= len(cars):
        return redirect("katalog")

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
            try:
                Booking.objects.create(
                    nama=nama,
                    mobil=car["name"],
                    tanggal=tanggal,
                    hari=hari,
                    total=total,
                    metode_pembayaran="bank",
                    status="menunggu"
                )
            except TypeError:
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


@login_required(login_url="login")
def history(request):
    data_booking = Booking.objects.all().order_by("-id")

    return render(request, "rental/history.html", {
        "history": data_booking
    })


@login_required(login_url="login")
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
@login_required(login_url="login")
def ai_chat(request):
    if request.method == "POST":
        try:
            if not GEMINI_API_KEY or client is None:
                return JsonResponse({
                    "reply": "API key Gemini belum ditemukan. Cek file .env dan pastikan GEMINI_API_KEY sudah diisi."
                })

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

            prompt = f"""
Kamu adalah asisten AI untuk website rental mobil SmartDrive.
Jawab dengan bahasa Indonesia yang ramah, singkat, jelas, dan mudah dipahami.

Tugas kamu:
- Membantu pelanggan memilih mobil berdasarkan jumlah orang, budget, kebutuhan, dan kenyamanan.
- Gunakan hanya data mobil yang tersedia.
- Jika pelanggan meminta mobil untuk 6 orang atau 7 orang, rekomendasikan mobil kapasitas 7 orang.
- Jika pelanggan ingin hemat, utamakan mobil dengan harga paling murah.
- Jangan menjawab terlalu panjang.

Data mobil yang tersedia:
{daftar_mobil}

Pertanyaan pelanggan:
{user_message}
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            jawaban = response.text

            if not jawaban:
                jawaban = "Maaf, AI belum memberikan jawaban. Silakan coba lagi."

            return JsonResponse({
                "reply": jawaban
            })

        except Exception as e:
            error_text = str(e)
            print("ERROR GEMINI:", error_text)

            if "API key not valid" in error_text or "API_KEY_INVALID" in error_text or "401" in error_text:
                return JsonResponse({
                    "reply": "API key Gemini tidak valid. Silakan cek kembali GEMINI_API_KEY di file .env."
                })

            if "429" in error_text or "quota" in error_text.lower() or "rate" in error_text.lower():
                return JsonResponse({
                    "reply": "Kuota atau limit gratis Gemini sedang habis/terbatas. Coba lagi nanti atau gunakan API key lain."
                })

            if "503" in error_text or "UNAVAILABLE" in error_text or "high demand" in error_text.lower():
                return JsonResponse({
                    "reply": "Model Gemini sedang ramai. Silakan coba lagi beberapa saat."
                })

            return JsonResponse({
                "reply": "Terjadi error API Gemini. Cek terminal VS Code untuk detail error-nya."
            })

    return JsonResponse({
        "reply": "Method tidak diizinkan."
    })