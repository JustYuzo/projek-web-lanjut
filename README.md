# SmartDrive

SmartDrive adalah aplikasi rental mobil berbasis web menggunakan **Django**. Aplikasi ini memiliki fitur katalog mobil, detail mobil, booking, pembayaran, upload bukti transfer, riwayat pesanan, verifikasi profil user, manajemen admin, stok mobil, dan AI rekomendasi mobil menggunakan Google Gemini API.

## Teknologi

- Python
- Django
- SQLite
- HTML, CSS, JavaScript
- Google Gemini API
- Pillow
- rembg
- Git & GitHub

## Fitur Utama

### User

- Daftar akun dan login.
- Melihat halaman home.
- Melihat katalog mobil.
- Filter mobil berdasarkan merek, kapasitas, dan harga.
- Melihat detail mobil.
- Melihat stok mobil.
- Booking mobil jika stok tersedia.
- Wajib melengkapi profil dan diverifikasi admin sebelum booking.
- Memilih pembayaran Transfer Bank atau E-Wallet.
- Upload bukti pembayaran.
- Melihat riwayat booking.
- Cetak kuitansi jika booking sudah selesai.
- Menggunakan AI rekomendasi mobil.

### Admin

- Login sebagai admin.
- Menambah, mengedit, dan menghapus mobil.
- Mengatur stok mobil.
- Melihat semua booking user.
- Mengubah status booking menjadi menunggu, diproses, selesai, atau ditolak.
- Memverifikasi atau menolak profil user.
- Melihat bukti pembayaran.
- Mencetak kuitansi admin.

## Alur Sistem User

```text
User membuka website
→ Melihat home
→ Masuk katalog mobil
→ Melihat detail mobil
→ Jika belum login, diarahkan ke login/signup
→ Jika sudah login, sistem cek profil
→ Jika profil belum terverifikasi, user melengkapi profil
→ Admin memverifikasi profil
→ User booking mobil
→ Pilih metode pembayaran
→ Upload bukti pembayaran
→ Booking masuk riwayat dengan status menunggu
→ Admin memproses booking
→ User melihat status terbaru di riwayat
```

## Alur Sistem Admin

```text
Admin login
→ Masuk dashboard admin
→ Mengelola data mobil dan stok
→ Membuka kelola booking
→ Mengecek bukti pembayaran
→ Mengubah status booking
→ Jika selesai, user bisa cetak kuitansi
→ Jika ditolak, stok mobil dikembalikan
```

## Alur Stok Mobil

```text
Admin mengisi stok mobil
→ Stok tampil di home, katalog, dan detail
→ User booking mobil
→ Stok berkurang 1
→ Jika stok 0, tombol booking nonaktif
→ Jika booking ditolak admin, stok kembali 1
```

## Alur Pembayaran

User dapat memilih dua metode pembayaran:

1. **Transfer Bank**
2. **E-Wallet / QRIS**

Pada pembayaran e-wallet, QRIS menggunakan file:

```text
static/images/qris.png
```

Setelah user mengunggah bukti pembayaran, booking akan masuk dengan status awal:

```text
menunggu
```

## AI Rekomendasi Mobil

Fitur AI digunakan untuk membantu user memilih mobil berdasarkan:

- Jumlah penumpang
- Budget
- Kebutuhan perjalanan

AI menggunakan Google Gemini API melalui `GEMINI_API_KEY` di file `.env`.

## Struktur Folder Singkat

```text
projek-web-lanjut/
├── manage.py
├── README.md
├── requirements.txt
├── rental/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── rental_mobil_ai/
│   ├── settings.py
│   └── urls.py
├── templates/
│   └── rental/
│       ├── home.html
│       ├── katalog.html
│       ├── detail.html
│       ├── payment.html
│       ├── payment_bank.html
│       ├── payment_ewallet.html
│       ├── history.html
│       ├── profil_user.html
│       ├── admin_mobil.html
│       ├── admin_booking.html
│       └── ai.html
├── static/
│   └── images/
└── media/
```

## Cara Menjalankan Project

### 1. Clone repository

```bash
git clone https://github.com/JustYuzo/projek-web-lanjut.git
cd projek-web-lanjut
```

### 2. Buat virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

### 4. Buat file `.env`

Buat file `.env` di root project:

```env
GEMINI_API_KEY=isi_api_key_gemini_kamu
```

### 5. Jalankan migrasi

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Buat akun admin

```bash
python manage.py createsuperuser
```

### 7. Jalankan server

```bash
python manage.py runserver
```

Buka browser:

```text
http://127.0.0.1:8000/
```

## Perintah Push ke GitHub

```bash
git status
git add .
git commit -m "update readme dan requirements"
git push origin main
```

## Kesimpulan

SmartDrive adalah sistem rental mobil berbasis Django yang memiliki alur lengkap mulai dari user melihat mobil, booking, pembayaran, upload bukti, riwayat, hingga admin mengelola mobil, stok, booking, dan verifikasi profil. Fitur AI rekomendasi membuat aplikasi lebih interaktif dan modern.
