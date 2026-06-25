from django import forms
from .models import Car, Profile


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "name",
            "brand",
            "transmission",
            "capacity",
            "price",
            "stock",
            "image",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Toyota Avanza Veloz"
            }),

            "brand": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Toyota"
            }),

            "transmission": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Manual / Automatic"
            }),

            "capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: 7",
                "min": "1"
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: 350000",
                "min": "0"
            }),

            "stock": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: 3",
                "min": "0"
            }),

            "image": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),
        }

        labels = {
            "name": "Nama Mobil",
            "brand": "Brand",
            "transmission": "Transmisi",
            "capacity": "Kapasitas",
            "price": "Harga Sewa per Hari",
            "stock": "Stok Mobil",
            "image": "Gambar Mobil",
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get("capacity")

        if capacity is None:
            return capacity

        if capacity < 1:
            raise forms.ValidationError("Kapasitas mobil minimal 1 orang.")

        return capacity

    def clean_price(self):
        price = self.cleaned_data.get("price")

        if price is None:
            return price

        if price < 0:
            raise forms.ValidationError("Harga sewa tidak boleh kurang dari 0.")

        return price

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")

        if stock is None:
            return 0

        if stock < 0:
            raise forms.ValidationError("Stok mobil tidak boleh kurang dari 0.")

        return stock


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = [
            "foto_profil",
            "nama_lengkap",
            "no_hp",
            "tempat_lahir",
            "tanggal_lahir",
            "jenis_kelamin",
            "nik_ktp",
            "foto_ktp",
            "nomor_sim_a",
            "masa_berlaku_sim",
            "foto_sim_a",
            "alamat_lengkap",
            "kota",
            "provinsi",
            "kode_pos",
            "kontak_darurat_nama",
            "kontak_darurat_no_hp",
            "kontak_darurat_hubungan",
        ]

        widgets = {
            "foto_profil": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),

            "nama_lengkap": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan nama lengkap sesuai KTP"
            }),

            "no_hp": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: 081234567890"
            }),

            "tempat_lahir": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Majene"
            }),

            "tanggal_lahir": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "jenis_kelamin": forms.Select(attrs={
                "class": "form-control"
            }),

            "nik_ktp": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan 16 digit NIK/KTP",
                "maxlength": "16"
            }),

            "foto_ktp": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),

            "nomor_sim_a": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan nomor SIM A"
            }),

            "masa_berlaku_sim": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "foto_sim_a": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),

            "alamat_lengkap": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Masukkan alamat lengkap"
            }),

            "kota": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Majene"
            }),

            "provinsi": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Sulawesi Barat"
            }),

            "kode_pos": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: 91412"
            }),

            "kontak_darurat_nama": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nama kontak darurat"
            }),

            "kontak_darurat_no_hp": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nomor HP kontak darurat"
            }),

            "kontak_darurat_hubungan": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Orang tua / Saudara / Teman"
            }),
        }

        labels = {
            "foto_profil": "Foto Profil",
            "nama_lengkap": "Nama Lengkap",
            "no_hp": "Nomor HP",
            "tempat_lahir": "Tempat Lahir",
            "tanggal_lahir": "Tanggal Lahir",
            "jenis_kelamin": "Jenis Kelamin",
            "nik_ktp": "NIK/KTP",
            "foto_ktp": "Foto KTP",
            "nomor_sim_a": "Nomor SIM A",
            "masa_berlaku_sim": "Masa Berlaku SIM A",
            "foto_sim_a": "Foto SIM A",
            "alamat_lengkap": "Alamat Lengkap",
            "kota": "Kota/Kabupaten",
            "provinsi": "Provinsi",
            "kode_pos": "Kode Pos",
            "kontak_darurat_nama": "Nama Kontak Darurat",
            "kontak_darurat_no_hp": "Nomor HP Kontak Darurat",
            "kontak_darurat_hubungan": "Hubungan Dengan Kontak Darurat",
        }

        error_messages = {
            "nik_ktp": {
                "unique": "NIK/KTP ini sudah digunakan oleh akun lain."
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Paksa 3 upload gambar memakai FileInput biasa.
        # Tujuannya agar tampilan default Django seperti "Saat ini / Hapus / Ubah" tidak muncul.
        file_fields = [
            "foto_profil",
            "foto_ktp",
            "foto_sim_a",
        ]

        for field in file_fields:
            self.fields[field].widget = forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            })
            self.fields[field].required = False

    def clean_nik_ktp(self):
        nik = self.cleaned_data.get("nik_ktp")

        if not nik:
            return None

        nik = nik.strip()

        if not nik.isdigit():
            raise forms.ValidationError("NIK/KTP harus berisi angka semua.")

        if len(nik) != 16:
            raise forms.ValidationError("NIK/KTP harus berisi tepat 16 digit.")

        return nik

    def clean_no_hp(self):
        no_hp = self.cleaned_data.get("no_hp")

        if no_hp:
            no_hp = no_hp.strip()

            angka_saja = no_hp.replace("+", "").replace("-", "").replace(" ", "")

            if not angka_saja.isdigit():
                raise forms.ValidationError("Nomor HP hanya boleh berisi angka, spasi, tanda +, atau tanda -.")

            if len(angka_saja) < 10:
                raise forms.ValidationError("Nomor HP minimal 10 digit.")

        return no_hp

    def clean_kontak_darurat_no_hp(self):
        no_hp = self.cleaned_data.get("kontak_darurat_no_hp")

        if no_hp:
            no_hp = no_hp.strip()

            angka_saja = no_hp.replace("+", "").replace("-", "").replace(" ", "")

            if not angka_saja.isdigit():
                raise forms.ValidationError("Nomor kontak darurat hanya boleh berisi angka, spasi, tanda +, atau tanda -.")

            if len(angka_saja) < 10:
                raise forms.ValidationError("Nomor kontak darurat minimal 10 digit.")

        return no_hp

    def clean_kode_pos(self):
        kode_pos = self.cleaned_data.get("kode_pos")

        if kode_pos:
            kode_pos = kode_pos.strip()

            if not kode_pos.isdigit():
                raise forms.ValidationError("Kode pos harus berisi angka.")

            if len(kode_pos) < 4:
                raise forms.ValidationError("Kode pos terlalu pendek.")

        return kode_pos


class AdminProfileStatusForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = [
            "status_verifikasi",
            "catatan_admin",
        ]

        widgets = {
            "status_verifikasi": forms.Select(attrs={
                "class": "form-control"
            }),

            "catatan_admin": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Tulis catatan admin jika profil ditolak atau perlu diperbaiki"
            }),
        }

        labels = {
            "status_verifikasi": "Status Verifikasi",
            "catatan_admin": "Catatan Admin",
        }
