from datetime import date, datetime, timedelta
import os
import json

from dotenv import load_dotenv
from google import genai

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt

from .models import Car, Booking
from .forms import CarForm


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def is_admin(user):
    return user.is_authenticated and user.is_staff


def get_cars_for_ai():
    cars_data = []

    for car in Car.objects.all().order_by("id"):
        cars_data.append({
            "id": car.id,
            "name": car.name,
            "price": car.price,
            "capacity": f"{car.capacity} Orang",
            "transmission": car.transmission,
            "status": "Tersedia",
            "brand": car.brand,
        })

    return cars_data


def home(request):
    cars = Car.objects.all().order_by("id")

    return render(request, "rental/home.html", {
        "cars": cars
    })


def katalog(request):
    cars = Car.objects.all().order_by("id")

    return render(request, "rental/katalog.html", {
        "cars": cars
    })


def detail_mobil(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    return render(request, "rental/detail.html", {
        "car": car
    })


def login_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_mobil")
        return redirect("home")

    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if email == "" or password == "":
            error = "Email dan kata sandi wajib diisi."
        else:
            user = None
            users_by_email = User.objects.filter(email=email)

            if users_by_email.exists():
                for user_obj in users_by_email:
                    user = authenticate(
                        request,
                        username=user_obj.username,
                        password=password
                    )

                    if user is not None:
                        break
            else:
                user = authenticate(
                    request,
                    username=email,
                    password=password
                )

            if user is not None:
                auth_login(request, user)

                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)

                if user.is_staff or user.is_superuser:
                    return redirect("admin_mobil")

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


def format_tanggal_indonesia(tanggal_date):
    bulan = [
        "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
    ]

    return f"{tanggal_date.day:02d} {bulan[tanggal_date.month - 1]} {tanggal_date.year}"


def hitung_payment_data(car, tanggal_mulai_input=None, hari=None, total=None, nama=None, user=None):
    if not tanggal_mulai_input:
        tanggal_mulai_input = date.today().strftime("%Y-%m-%d")

    try:
        durasi = int(hari)
    except (TypeError, ValueError):
        durasi = 1

    if durasi < 1:
        durasi = 1

    try:
        total_final = int(total)
    except (TypeError, ValueError):
        total_final = car.price * durasi

    try:
        tanggal_mulai_date = datetime.strptime(tanggal_mulai_input, "%Y-%m-%d").date()
    except ValueError:
        tanggal_mulai_date = date.today()
        tanggal_mulai_input = tanggal_mulai_date.strftime("%Y-%m-%d")

    tanggal_selesai_date = tanggal_mulai_date + timedelta(days=durasi - 1)

    nama_final = nama
    if not nama_final and user is not None:
        nama_final = user.get_full_name() or user.username

    return {
        "nama": nama_final or "",
        "tanggal_mulai_input": tanggal_mulai_input,
        "tanggal_mulai_text": format_tanggal_indonesia(tanggal_mulai_date),
        "tanggal_selesai_text": format_tanggal_indonesia(tanggal_selesai_date),
        "durasi": durasi,
        "total": total_final,
    }


def get_payment_context(request, car):
    session_data = request.session.get(f"payment_data_{car.id}", {})

    payment_data = hitung_payment_data(
        car=car,
        tanggal_mulai_input=session_data.get("tanggal"),
        hari=session_data.get("hari"),
        total=session_data.get("total"),
        nama=session_data.get("nama"),
        user=request.user,
    )

    return {
        "car": car,
        "today": date.today(),
        **payment_data,
    }


@login_required(login_url="login")
def payment(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    car = get_object_or_404(Car, id=car_id)

    # Saat user kembali ke halaman payment, pakai data awal 1 hari.
    payment_data = hitung_payment_data(
        car=car,
        tanggal_mulai_input=date.today().strftime("%Y-%m-%d"),
        hari=1,
        total=car.price,
        user=request.user,
    )

    return render(request, "rental/payment.html", {
        "car": car,
        "today": date.today(),
        **payment_data,
    })


@login_required(login_url="login")
def booking(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        nama = request.POST.get("nama", "").strip()
        tanggal = request.POST.get("tanggal") or date.today().strftime("%Y-%m-%d")
        hari = request.POST.get("hari", 1)
        total = request.POST.get("total")
        payment_method = request.POST.get("payment_method", "Transfer Bank")

        if nama == "":
            nama = request.user.get_full_name() or request.user.username

        payment_data = hitung_payment_data(
            car=car,
            tanggal_mulai_input=tanggal,
            hari=hari,
            total=total,
            nama=nama,
            user=request.user,
        )

        request.session[f"payment_data_{car.id}"] = {
            "nama": payment_data["nama"],
            "tanggal": payment_data["tanggal_mulai_input"],
            "hari": payment_data["durasi"],
            "total": payment_data["total"],
            "payment_method": payment_method,
        }

        request.session.modified = True

        if payment_method == "E-Wallet":
            return redirect("payment_ewallet", car_id=car.id)

        return redirect("payment_bank", car_id=car.id)

    return redirect("payment", car_id=car.id)


@login_required(login_url="login")
def payment_bank(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    car = get_object_or_404(Car, id=car_id)
    context = get_payment_context(request, car)

    return render(request, "rental/payment_bank.html", context)


@login_required(login_url="login")
def payment_ewallet(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    car = get_object_or_404(Car, id=car_id)
    context = get_payment_context(request, car)

    return render(request, "rental/payment_ewallet.html", context)


@login_required(login_url="login")
def konfirmasi_payment(request, car_id, metode):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        session_data = request.session.get(f"payment_data_{car.id}", {})

        nama = request.POST.get("nama") or session_data.get("nama") or request.user.get_full_name() or request.user.username
        tanggal = request.POST.get("tanggal") or session_data.get("tanggal") or date.today().strftime("%Y-%m-%d")
        hari = request.POST.get("hari") or session_data.get("hari") or 1
        total = request.POST.get("total") or session_data.get("total")

        payment_data = hitung_payment_data(
            car=car,
            tanggal_mulai_input=tanggal,
            hari=hari,
            total=total,
            nama=nama,
            user=request.user,
        )

        if metode == "bank":
            metode_pembayaran = "Transfer Bank"
        elif metode == "ewallet":
            metode_pembayaran = "E-Wallet"
        else:
            metode_pembayaran = metode

        Booking.objects.create(
            user=request.user,
            car=car,
            nama=payment_data["nama"],
            mobil=car.name,
            tanggal=payment_data["tanggal_mulai_input"],
            hari=payment_data["durasi"],
            total=payment_data["total"],
            metode_pembayaran=metode_pembayaran,
            status="menunggu"
        )

        request.session.pop(f"payment_data_{car.id}", None)
        request.session.modified = True

        return redirect("history")

    return redirect("payment", car_id=car.id)


@login_required(login_url="login")
def history(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "rental/history.html", {
        "bookings": bookings,
        "total_booking": bookings.count(),
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_mobil(request):
    cars = Car.objects.all().order_by("-id")

    return render(request, "rental/admin_mobil.html", {
        "cars": cars
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_tambah_mobil(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("admin_mobil")
    else:
        form = CarForm()

    return render(request, "rental/admin_form_mobil.html", {
        "form": form,
        "title": "Tambah Mobil",
        "button_text": "Simpan Mobil"
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_edit_mobil(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)

        if form.is_valid():
            form.save()
            return redirect("admin_mobil")
    else:
        form = CarForm(instance=car)

    return render(request, "rental/admin_form_mobil.html", {
        "form": form,
        "car": car,
        "title": "Edit Mobil",
        "button_text": "Update Mobil"
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_hapus_mobil(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        car.delete()
        return redirect("admin_mobil")

    return render(request, "rental/admin_hapus_mobil.html", {
        "car": car
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_booking(request):
    bookings = Booking.objects.all().order_by("-created_at")

    return render(request, "rental/admin_booking.html", {
        "bookings": bookings
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_update_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        status = request.POST.get("status")

        if status in ["menunggu", "diproses", "selesai", "ditolak"]:
            booking.status = status
            booking.save()

    return redirect("admin_booking")


@login_required(login_url="login")
def ai_rekomendasi(request):
    hasil = []
    pesan = None
    cars_data = get_cars_for_ai()

    if request.method == "POST":
        try:
            jumlah_orang = int(request.POST.get("jumlah_orang", 1))
        except ValueError:
            jumlah_orang = 1

        try:
            budget = int(request.POST.get("budget", 100000))
        except ValueError:
            budget = 100000

        kebutuhan = request.POST.get("kebutuhan")

        for car in cars_data:
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
    cars_data = []

    for car in Car.objects.all().order_by("id"):
        cars_data.append({
            "id": car.id,
            "name": car.name,
            "brand": car.brand,
            "price": car.price,
            "capacity": car.capacity,
            "transmission": car.transmission,
            "image": car.image.url if car.image else None,
        })

    return JsonResponse({
        "status": "success",
        "message": "Data mobil berhasil diambil",
        "data": cars_data
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

            cars_data = get_cars_for_ai()

            daftar_mobil = ""
            for car in cars_data:
                daftar_mobil += (
                    f"- {car['name']}, brand {car['brand']}, "
                    f"harga Rp {car['price']:,}/hari, "
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
