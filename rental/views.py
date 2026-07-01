from datetime import date, datetime, timedelta
import os
import json
import random

from dotenv import load_dotenv
from google import genai

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction

from .models import Car, Booking, Profile
from .forms import CarForm, ProfileForm, AdminProfileStatusForm


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# HELPER
# =========================

def is_admin(user):
    return user.is_authenticated and user.is_staff


def user_profile_sudah_terverifikasi(user):
    try:
        return user.profile.status_verifikasi == Profile.STATUS_TERVERIFIKASI
    except Profile.DoesNotExist:
        return False


def generate_kode_unik():
    return random.randint(100, 999)


def get_cars_for_ai():
    cars_data = []

    for car in Car.objects.all().order_by("id"):
        cars_data.append({
            "id": car.id,
            "name": car.name,
            "price": car.price,
            "capacity": f"{car.capacity} Orang",
            "transmission": car.transmission,
            "status": car.status_stok,
            "brand": car.brand,
            "stock": car.stock,
            "tersedia": car.tersedia,
        })

    return cars_data


def format_tanggal_indonesia(tanggal_date):
    bulan = [
        "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
    ]

    return f"{tanggal_date.day:02d} {bulan[tanggal_date.month - 1]} {tanggal_date.year}"


def hitung_payment_data(
    car,
    tanggal_mulai_input=None,
    hari=None,
    total=None,
    nama=None,
    user=None,
    kode_unik=None
):
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

    try:
        kode_unik_final = int(kode_unik)
    except (TypeError, ValueError):
        kode_unik_final = generate_kode_unik()

    total_bayar = total_final + kode_unik_final

    return {
        "nama": nama_final or "",
        "tanggal_mulai_input": tanggal_mulai_input,
        "tanggal_mulai_text": format_tanggal_indonesia(tanggal_mulai_date),
        "tanggal_selesai_text": format_tanggal_indonesia(tanggal_selesai_date),
        "durasi": durasi,
        "total": total_final,
        "kode_unik": kode_unik_final,
        "total_bayar": total_bayar,
    }


def get_payment_context(request, car):
    session_key = f"payment_data_{car.id}"
    session_data = request.session.get(session_key, {})

    if not session_data.get("kode_unik"):
        session_data["kode_unik"] = generate_kode_unik()
        request.session[session_key] = session_data
        request.session.modified = True

    payment_data = hitung_payment_data(
        car=car,
        tanggal_mulai_input=session_data.get("tanggal"),
        hari=session_data.get("hari"),
        total=session_data.get("total"),
        nama=session_data.get("nama"),
        user=request.user,
        kode_unik=session_data.get("kode_unik"),
    )

    request.session[session_key] = {
        "nama": payment_data["nama"],
        "tanggal": payment_data["tanggal_mulai_input"],
        "hari": payment_data["durasi"],
        "total": payment_data["total"],
        "kode_unik": payment_data["kode_unik"],
        "total_bayar": payment_data["total_bayar"],
        "payment_method": session_data.get("payment_method", "Transfer Bank"),
    }
    request.session.modified = True

    return {
        "car": car,
        "today": date.today(),
        **payment_data,
    }


def booking_boleh_dilanjutkan(request, car):
    if car.stock <= 0:
        messages.error(
            request,
            f"Maaf, stok {car.name} sedang habis. Silakan pilih mobil lain."
        )
        return False

    return True


def proses_stock_saat_status_berubah(booking, status_baru):
    """
    Aturan stok:
    - Saat booking dibuat, stok dikurangi 1 dan stock_dikurangi=True.
    - Jika admin menolak booking, stok dikembalikan 1 dan stock_dikurangi=False.
    - Jika booking yang sudah ditolak diaktifkan lagi, stok dikurangi kembali jika masih tersedia.
    """
    if status_baru == "ditolak":
        if booking.stock_dikurangi and booking.car:
            booking.car.tambah_stock()
            booking.stock_dikurangi = False

        return True, "Stok mobil dikembalikan karena booking ditolak."

    if not booking.stock_dikurangi and booking.car:
        berhasil = booking.car.kurangi_stock()

        if not berhasil:
            return False, f"Stok {booking.car.name} sedang habis. Status booking tidak dapat diubah."

        booking.stock_dikurangi = True

    return True, "Stok booking sudah sesuai."

    # --- FUNGSI AI (TAMBAHAN) ---
def analyze_image_with_gemini(image_file, prompt):
    try:
        if not client: return None
        image_bytes = image_file.read()
        image_file.seek(0)
        mime_type = image_file.content_type if image_file.content_type else "image/jpeg"
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, {"mime_type": mime_type, "data": image_bytes}]
        )
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# =========================
# HALAMAN USER
# =========================

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


# =========================
# AUTH
# =========================

def login_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_mobil")
        return redirect("home")

    next_url = request.GET.get("next", "")
    error = None

    if next_url:
        if "payment" in next_url or "booking" in next_url or "konfirmasi" in next_url:
            error = "Silakan login atau daftar akun terlebih dahulu sebelum melakukan booking mobil."
        else:
            error = "Silakan login terlebih dahulu untuk melanjutkan."

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

                Profile.objects.get_or_create(user=user)

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
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nama_depan,
                last_name=nama_belakang
            )

            profile, created = Profile.objects.get_or_create(user=user)
            profile.nama_lengkap = f"{nama_depan} {nama_belakang}".strip()
            profile.no_hp = no_telpon
            profile.save()

            return redirect("login")

    return render(request, "rental/signup.html", {
        "error": error
    })


def logout_page(request):
    auth_logout(request)
    return redirect("login")


# =========================
# PROFIL USER
# =========================

@login_required(login_url="login")
def profil_user(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_profile")

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            profile = form.save(commit=False)

            if profile.data_lengkap():
                if profile.status_verifikasi == Profile.STATUS_TERVERIFIKASI:
                    profile.status_verifikasi = Profile.STATUS_MENUNGGU
                    profile.catatan_admin = "Profil diperbarui oleh user. Menunggu verifikasi ulang admin."
                    profile.diverifikasi_oleh = None
                    profile.tanggal_verifikasi = None

                elif profile.status_verifikasi in [
                    Profile.STATUS_BELUM_LENGKAP,
                    Profile.STATUS_DITOLAK,
                    Profile.STATUS_MENUNGGU
                ]:
                    profile.status_verifikasi = Profile.STATUS_MENUNGGU
            else:
                profile.status_verifikasi = Profile.STATUS_BELUM_LENGKAP

            profile.save()

            messages.success(
                request,
                "Profil berhasil disimpan. Jika data sudah lengkap, profil akan menunggu verifikasi admin."
            )
            return redirect("profil_user")

        else:
            messages.error(
                request,
                "Profil gagal disimpan. Periksa kembali data yang diisi."
            )

    else:
        form = ProfileForm(instance=profile)

    return render(request, "rental/profil_user.html", {
        "profile": profile,
        "form": form,
    })


# =========================
# PAYMENT DAN BOOKING
# =========================

@login_required(login_url="login")
def payment(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.bisa_booking():
        messages.warning(
            request,
            "Lengkapi profil dan tunggu verifikasi admin sebelum melakukan booking mobil."
        )
        return redirect("profil_user")

    car = get_object_or_404(Car, id=car_id)

    if not booking_boleh_dilanjutkan(request, car):
        return redirect("katalog")

    kode_unik = generate_kode_unik()

    payment_data = hitung_payment_data(
        car=car,
        tanggal_mulai_input=date.today().strftime("%Y-%m-%d"),
        hari=1,
        total=car.price,
        user=request.user,
        kode_unik=kode_unik,
    )

    request.session[f"payment_data_{car.id}"] = {
        "nama": payment_data["nama"],
        "tanggal": payment_data["tanggal_mulai_input"],
        "hari": payment_data["durasi"],
        "total": payment_data["total"],
        "kode_unik": payment_data["kode_unik"],
        "total_bayar": payment_data["total_bayar"],
        "payment_method": "Transfer Bank",
    }
    request.session.modified = True

    return render(request, "rental/payment.html", {
        "car": car,
        "today": date.today(),
        **payment_data,
    })


@login_required(login_url="login")
def booking(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.bisa_booking():
        messages.warning(
            request,
            "Lengkapi profil dan tunggu verifikasi admin sebelum melakukan booking mobil."
        )
        return redirect("profil_user")

    car = get_object_or_404(Car, id=car_id)

    if not booking_boleh_dilanjutkan(request, car):
        return redirect("katalog")

    if request.method == "POST":
        nama = request.POST.get("nama", "").strip()
        tanggal = request.POST.get("tanggal") or date.today().strftime("%Y-%m-%d")
        hari = request.POST.get("hari", 1)
        total = request.POST.get("total")
        payment_method = request.POST.get("payment_method", "Transfer Bank")

        if nama == "":
            nama = request.user.get_full_name() or request.user.username

        kode_unik = generate_kode_unik()

        payment_data = hitung_payment_data(
            car=car,
            tanggal_mulai_input=tanggal,
            hari=hari,
            total=total,
            nama=nama,
            user=request.user,
            kode_unik=kode_unik,
        )

        request.session[f"payment_data_{car.id}"] = {
            "nama": payment_data["nama"],
            "tanggal": payment_data["tanggal_mulai_input"],
            "hari": payment_data["durasi"],
            "total": payment_data["total"],
            "kode_unik": payment_data["kode_unik"],
            "total_bayar": payment_data["total_bayar"],
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

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.bisa_booking():
        messages.warning(
            request,
            "Lengkapi profil dan tunggu verifikasi admin sebelum melakukan booking mobil."
        )
        return redirect("profil_user")

    car = get_object_or_404(Car, id=car_id)

    if not booking_boleh_dilanjutkan(request, car):
        return redirect("katalog")

    context = get_payment_context(request, car)

    return render(request, "rental/payment_bank.html", context)


@login_required(login_url="login")
def payment_ewallet(request, car_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.bisa_booking():
        messages.warning(
            request,
            "Lengkapi profil dan tunggu verifikasi admin sebelum melakukan booking mobil."
        )
        return redirect("profil_user")

    car = get_object_or_404(Car, id=car_id)

    if not booking_boleh_dilanjutkan(request, car):
        return redirect("katalog")

    context = get_payment_context(request, car)

    return render(request, "rental/payment_ewallet.html", context)


@login_required(login_url="login")
def konfirmasi_payment(request, car_id, metode):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_mobil")

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.bisa_booking():
        messages.warning(
            request,
            "Lengkapi profil dan tunggu verifikasi admin sebelum melakukan booking mobil."
        )
        return redirect("profil_user")

    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        session_data = request.session.get(f"payment_data_{car.id}", {})

        nama = (
            request.POST.get("nama")
            or session_data.get("nama")
            or request.user.get_full_name()
            or request.user.username
        )

        tanggal = (
            request.POST.get("tanggal")
            or session_data.get("tanggal")
            or date.today().strftime("%Y-%m-%d")
        )

        hari = request.POST.get("hari") or session_data.get("hari") or 1
        total = request.POST.get("total") or session_data.get("total") or car.price
        kode_unik = request.POST.get("kode_unik") or session_data.get("kode_unik") or generate_kode_unik()

        bukti_transfer = request.FILES.get("bukti_transfer")

        bank_pembayaran = (
            request.POST.get("bank_pembayaran")
            or request.POST.get("bank")
            or request.POST.get("ewallet")
            or request.POST.get("nama_bank")
            or request.POST.get("metode_detail")
            or ""
        )

        payment_data = hitung_payment_data(
            car=car,
            tanggal_mulai_input=tanggal,
            hari=hari,
            total=total,
            nama=nama,
            user=request.user,
            kode_unik=kode_unik,
        )

        if metode == "bank":
            metode_pembayaran = "Transfer Bank"
        elif metode == "ewallet":
            metode_pembayaran = "E-Wallet"
        else:
            metode_pembayaran = metode

        with transaction.atomic():
            car = Car.objects.select_for_update().get(id=car.id)

            if car.stock <= 0:
                messages.error(
                    request,
                    f"Maaf, stok {car.name} sudah habis. Booking tidak dapat dibuat."
                )
                return redirect("katalog")

            car.stock -= 1
            car.save(update_fields=["stock"])

            Booking.objects.create(
                user=request.user,
                car=car,
                nama=payment_data["nama"],
                mobil=car.name,
                tanggal=payment_data["tanggal_mulai_input"],
                hari=payment_data["durasi"],
                total=payment_data["total"],
                metode_pembayaran=metode_pembayaran,
                bank_pembayaran=bank_pembayaran,
                bukti_transfer=bukti_transfer,
                kode_unik=payment_data["kode_unik"],
                total_bayar=payment_data["total_bayar"],
                stock_dikurangi=True,
                status="menunggu"
            )

        request.session.pop(f"payment_data_{car.id}", None)
        request.session.modified = True

        messages.success(
            request,
            "Booking berhasil dibuat. Pembayaran kamu sedang menunggu konfirmasi admin."
        )

        return redirect("history")

    return redirect("payment", car_id=car.id)


@login_required(login_url="login")
def history(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "rental/history.html", {
        "bookings": bookings,
        "total_booking": bookings.count(),
    })


# =========================
# KUITANSI USER DAN ADMIN
# =========================

@login_required(login_url="login")
def cetak_kuitansi_user(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("user", "car"),
        id=booking_id,
        user=request.user
    )

    if booking.status != "selesai":
        messages.warning(
            request,
            "Kuitansi belum bisa dicetak karena pembayaran belum berhasil dikonfirmasi admin."
        )
        return redirect("history")

    return render(request, "rental/kuitansi.html", {
        "booking": booking,
        "is_admin_receipt": False,
        "judul_kuitansi": "Kuitansi Pembayaran",
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def cetak_kuitansi_admin(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("user", "car"),
        id=booking_id
    )

    if booking.status != "selesai":
        messages.warning(
            request,
            "Kuitansi belum bisa dicetak karena pembayaran booking ini belum berstatus berhasil."
        )
        return redirect("admin_booking")

    return render(request, "rental/kuitansi.html", {
        "booking": booking,
        "is_admin_receipt": True,
        "judul_kuitansi": "Kuitansi Pembayaran Admin",
    })


# =========================
# ADMIN MOBIL
# =========================

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
            messages.success(request, "Mobil berhasil ditambahkan.")
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
            messages.success(request, "Data mobil berhasil diperbarui.")
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
        messages.success(request, "Mobil berhasil dihapus.")
        return redirect("admin_mobil")

    return render(request, "rental/admin_hapus_mobil.html", {
        "car": car
    })


# =========================
# ADMIN BOOKING
# =========================

@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_booking(request):
    bookings = Booking.objects.select_related("user", "car").all().order_by("-created_at")

    total_booking = bookings.count()
    total_menunggu = bookings.filter(status="menunggu").count()
    total_diproses = bookings.filter(status="diproses").count()
    total_selesai = bookings.filter(status="selesai").count()
    total_ditolak = bookings.filter(status="ditolak").count()

    pendapatan = 0
    for booking in bookings.filter(status="selesai"):
        if hasattr(booking, "total_bayar") and booking.total_bayar:
            pendapatan += booking.total_bayar
        else:
            pendapatan += booking.total

    return render(request, "rental/admin_booking.html", {
        "bookings": bookings,
        "total_booking": total_booking,
        "total_menunggu": total_menunggu,
        "total_diproses": total_diproses,
        "total_selesai": total_selesai,
        "total_ditolak": total_ditolak,
        "pendapatan": pendapatan,
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_update_status(request, booking_id):
    if request.method == "POST":
        status = request.POST.get("status")

        if status in ["menunggu", "diproses", "selesai", "ditolak"]:
            with transaction.atomic():
                booking = get_object_or_404(
                    Booking.objects.select_for_update().select_related("car"),
                    id=booking_id
                )

                status_lama = booking.status

                if status_lama == status:
                    messages.info(
                        request,
                        f"Status booking {booking.nama} tidak berubah."
                    )
                    return redirect("admin_booking")

                berhasil, pesan_stock = proses_stock_saat_status_berubah(booking, status)

                if not berhasil:
                    messages.error(request, pesan_stock)
                    return redirect("admin_booking")

                booking.status = status
                booking.save(update_fields=["status", "stock_dikurangi", "updated_at"])

            messages.success(
                request,
                f"Status booking {booking.nama} berhasil diperbarui. {pesan_stock}"
            )
        else:
            messages.error(request, "Status booking tidak valid.")

    return redirect("admin_booking")


# =========================
# ADMIN PROFILE USER
# =========================

@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_profile(request):
    status = request.GET.get("status", "")

    profiles = Profile.objects.select_related("user").all().order_by("-diperbarui_pada")

    if status:
        profiles = profiles.filter(status_verifikasi=status)

    total_profile = Profile.objects.count()

    total_belum_lengkap = Profile.objects.filter(
        status_verifikasi=Profile.STATUS_BELUM_LENGKAP
    ).count()

    total_menunggu = Profile.objects.filter(
        status_verifikasi=Profile.STATUS_MENUNGGU
    ).count()

    total_terverifikasi = Profile.objects.filter(
        status_verifikasi=Profile.STATUS_TERVERIFIKASI
    ).count()

    total_ditolak = Profile.objects.filter(
        status_verifikasi=Profile.STATUS_DITOLAK
    ).count()

    return render(request, "rental/admin_profile.html", {
        "profiles": profiles,
        "status": status,
        "total_profile": total_profile,
        "total_belum_lengkap": total_belum_lengkap,
        "total_menunggu": total_menunggu,
        "total_terverifikasi": total_terverifikasi,
        "total_ditolak": total_ditolak,
        "status_choices": Profile.STATUS_CHOICES,
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_profile_detail(request, profile_id):
    profile = get_object_or_404(
        Profile.objects.select_related("user", "diverifikasi_oleh"),
        id=profile_id
    )

    form = AdminProfileStatusForm(instance=profile)

    return render(request, "rental/admin_profile_detail.html", {
        "profile": profile,
        "form": form,
        "status_choices": Profile.STATUS_CHOICES,
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_update_profile_status(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == "POST":
        form = AdminProfileStatusForm(request.POST, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)

            if profile.status_verifikasi in [
                Profile.STATUS_TERVERIFIKASI,
                Profile.STATUS_DITOLAK
            ]:
                profile.diverifikasi_oleh = request.user
                profile.tanggal_verifikasi = timezone.now()
            else:
                profile.diverifikasi_oleh = None
                profile.tanggal_verifikasi = None

            profile.save()

            if profile.status_verifikasi == Profile.STATUS_TERVERIFIKASI:
                messages.success(
                    request,
                    "Profil user berhasil diverifikasi. User sekarang bisa melakukan booking mobil."
                )

            elif profile.status_verifikasi == Profile.STATUS_DITOLAK:
                messages.warning(
                    request,
                    "Profil user ditolak. Catatan admin sudah disimpan."
                )

            elif profile.status_verifikasi == Profile.STATUS_MENUNGGU:
                messages.info(
                    request,
                    "Status profil dikembalikan ke menunggu verifikasi."
                )

            else:
                messages.info(
                    request,
                    "Status profil diubah menjadi belum lengkap."
                )

        else:
            messages.error(
                request,
                "Gagal memperbarui status profil. Periksa kembali input admin."
            )

    return redirect("admin_profile_detail", profile_id=profile.id)


# =========================
# AI REKOMENDASI
# =========================

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
            if not car.get("tersedia"):
                continue

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


# =========================
# API MOBIL
# =========================

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
            "stock": car.stock,
            "status_stok": car.status_stok,
            "tersedia": car.tersedia,
            "image": car.image.url if car.image else None,
        })

    return JsonResponse({
        "status": "success",
        "message": "Data mobil berhasil diambil",
        "data": cars_data
    })


# =========================
# AI CHAT GEMINI
# =========================

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