import streamlit as st
import datetime

st.set_page_config(page_title="Rental Mobil AI", page_icon="🚗", layout="wide")

if "history" not in st.session_state:
    st.session_state["history"] = []

cars = [
    {"name": "Toyota Avanza", "price": 350000, "capacity": "7 Orang", "transmission": "Manual", "status": "Tersedia", "image": "🚙"},
    {"name": "Honda Brio", "price": 300000, "capacity": "5 Orang", "transmission": "Matic", "status": "Tersedia", "image": "🚗"},
    {"name": "Toyota Innova", "price": 500000, "capacity": "7 Orang", "transmission": "Matic", "status": "Tersedia", "image": "🚘"},
]

st.markdown("""
<style>
.stApp { background-color: #0f1117; }

.main-title { font-size: 50px; font-weight: 800; color: white; }
.subtitle { font-size: 20px; color: #d1d5db; margin-bottom: 35px; }

.car-card {
    background-color: #171923;
    border: 1px solid #2d3748;
    border-radius: 18px;
    padding: 24px;
    min-height: 430px;
}

.car-img {
    height: 160px;
    background: #111827;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 90px;
    margin-bottom: 25px;
}

.car-name { color: white; font-size: 28px; font-weight: 800; margin-bottom: 18px; }
.car-info { color: #e5e7eb; font-size: 18px; margin-bottom: 12px; }

.status {
    background: #14532d;
    color: #86efac;
    padding: 14px;
    border-radius: 12px;
    font-size: 17px;
    margin-top: 18px;
    margin-bottom: 18px;
}

.ai-box {
    background-color: #171923;
    border: 1px solid #2d3748;
    border-radius: 18px;
    padding: 20px;
    margin-top: 15px;
}

.history-box {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
    font-size: 17px;
    font-weight: 700;
    background-color: #2563eb;
    color: white;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚗 Rental Mobil AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Temukan mobil rental terbaik untuk perjalananmu.</div>', unsafe_allow_html=True)

st.markdown("## Daftar Mobil")
cols = st.columns(3)

for i, car in enumerate(cars):
    with cols[i]:
        st.markdown(
            f"""
            <div class="car-card">
                <div class="car-img">{car['image']}</div>
                <div class="car-name">{car['name']}</div>
                <div class="car-info">💰 Rp {car['price']:,} / hari</div>
                <div class="car-info">👥 {car['capacity']}</div>
                <div class="car-info">⚙️ {car['transmission']}</div>
                <div class="status">{car['status']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Booking", key=f"booking_{i}"):
            st.session_state["selected_car"] = car

st.divider()

if "selected_car" in st.session_state:
    selected = st.session_state["selected_car"]

    st.markdown("## 📝 Form Booking")
    st.write(f"Mobil: **{selected['name']}**")
    st.write(f"Harga per hari: **Rp {selected['price']:,}**")

    nama = st.text_input("Nama Penyewa")
    tanggal = st.date_input("Tanggal Sewa", min_value=datetime.date.today())
    hari = st.number_input("Jumlah Hari", min_value=1, step=1)

    total = selected["price"] * hari
    st.info(f"Total: Rp {total:,}")

    if st.button("Konfirmasi Booking"):
        if nama.strip() == "":
            st.error("Nama harus diisi")
        elif tanggal < datetime.date.today():
            st.error("Tanggal sewa tidak boleh sebelum hari ini")
        else:
            data = {
                "nama": nama.strip(),
                "mobil": selected["name"],
                "tanggal": tanggal,
                "hari": hari,
                "total": total
            }

            st.session_state["history"].append(data)
            del st.session_state["selected_car"]

            st.success(f"Booking berhasil! Total Rp {total:,}")

st.divider()

st.markdown("## 🤖 AI Rekomendasi Mobil")

jumlah_orang = st.number_input("Jumlah Orang", min_value=1)
budget = st.number_input("Budget per Hari", min_value=100000, step=50000)
kebutuhan = st.selectbox("Kebutuhan", ["Hemat", "Keluarga", "Nyaman"])

def rekomendasi(cars, orang, budget, kebutuhan):
    hasil = []

    for car in cars:
        kapasitas = int(car["capacity"].split()[0])

        if kapasitas >= orang and car["price"] <= budget:
            if kebutuhan == "Hemat" and car["price"] <= 350000:
                hasil.append(car)
            elif kebutuhan == "Keluarga" and kapasitas >= 7:
                hasil.append(car)
            elif kebutuhan == "Nyaman":
                hasil.append(car)

    return hasil

if st.button("Cari Rekomendasi"):
    hasil = rekomendasi(cars, jumlah_orang, budget, kebutuhan)

    if hasil:
        st.success("Mobil yang cocok untuk kamu:")
        for car in hasil:
            st.markdown(
                f"""
                <div class="ai-box">
                    <b>{car['image']} {car['name']}</b><br>
                    💰 Rp {car['price']:,} / hari<br>
                    👥 {car['capacity']}<br>
                    ⚙️ {car['transmission']}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning("Tidak ada mobil yang cocok")

st.divider()

st.markdown("## 📜 Riwayat Booking")

if st.session_state["history"]:
    if st.button("Hapus Semua Riwayat"):
        st.session_state["history"] = []
        st.rerun()

    for h in st.session_state["history"]:
        st.markdown(
            f"""
            <div class="history-box">
                👤 {h['nama']} <br>
                🚗 {h['mobil']} <br>
                📅 {h['tanggal']} <br>
                ⏳ {h['hari']} hari <br>
                💰 Rp {h['total']:,}
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("Belum ada booking")