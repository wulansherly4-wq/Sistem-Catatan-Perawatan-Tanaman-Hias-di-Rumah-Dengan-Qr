# main.py
import streamlit as st
import pandas as pd
from utils import *
from qr_utils import *

# ===== IMPORT KAMERA (OPENCV) =====
import cv2
import numpy as np
from PIL import Image

# ===== IMPORT PLOTLY (UNTUK GRAFIK INTERAKTIF) =====
import plotly.express as px

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="🌿 Sistem Perawatan Tanaman Hias",
    layout="wide"
)

# ===== CSS TEMA HIJAU (KONTRAS JELAS) =====
st.markdown("""
<style>
/* Background utama */
.stApp {
    background-color: #1B5E20;
}

/* Judul */
h1, h2, h3 {
    color: #E8F5E9;
}

/* Text biasa */
p, label, span, div {
    color: #F1F8E9 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #2E7D32;
}

/* Card metric */
[data-testid="metric-container"] {
    background-color: #388E3C;
    border-radius: 12px;
    padding: 15px;
    color: white;
}

/* Tombol */
.stButton > button {
    background-color: #66BB6A;
    color: #1B5E20;
    font-weight: bold;
    border-radius: 8px;
}

/* Input */
input, textarea {
    background-color: #E8F5E9 !important;
    color: #1B5E20 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# ===== LOGIN =====
if "login" not in st.session_state:
    st.session_state.login = False

def login_page():
    st.title("🔐 Login Sistem 🌱")
    user = st.text_input("👤 Username")
    pwd = st.text_input("🔑 Password", type="password")

    if st.button("🚪 Login"):
        if user == "sepentin" and pwd == "12345678":
            st.session_state.login = True
            st.success("✅ Login berhasil")
            st.rerun()
        else:
            st.error("❌ Username atau password salah")

if not st.session_state.login:
    login_page()
    st.stop()

# ===== SETUP DATA =====
ensure_data_files()

# ===== MENU =====
menu = st.sidebar.selectbox(
    "📌 Menu Utama",
    [
        "🌿 Dashboard",
        "📋 Data Master (CRUD)",
        "🔖 Generate QR",
        "📷 Scan QR / Input Manual",
        "📊 Grafik / Laporan",
        "ℹ Tentang"
    ]
)

# ================= DASHBOARD =================
if menu == "🌿 Dashboard":
    st.title("🌿 Dashboard Perawatan Tanaman")

    df = load_data()
    c1, c2, c3 = st.columns(3)

    c1.metric("🪴 Total Tanaman", len(df))
    c2.metric("🧪 Jenis Pupuk", df["jenis_pupuk"].nunique() if not df.empty else 0)
    c3.metric("💧 Terakhir Disiram", df["tanggal_siram_terakhir"].max() if not df.empty else "-")

    st.markdown("---")
    
    # --- BAGIAN GRAFIK DIGANTI KE PLOTLY ---
    if not df.empty:
        # Menghitung jumlah per jenis pupuk
        data_grafik = df['jenis_pupuk'].value_counts().reset_index()
        data_grafik.columns = ['Jenis Pupuk', 'Jumlah']
        
        # Membuat Chart Plotly
        fig = px.bar(
            data_grafik, 
            x='Jenis Pupuk', 
            y='Jumlah',
            title='Jumlah Tanaman per Jenis Pupuk',
            text='Jumlah',
            color='Jenis Pupuk',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig.update_layout(xaxis_title="Jenis Pupuk", yaxis_title="Jumlah Tanaman")
        st.plotly_chart(fig, use_container_width=True)

# ================= CRUD =================
elif menu == "📋 Data Master (CRUD)":
    st.title("📋 Data Master Tanaman Hias 🌸")

    df = load_data()
    ids = ["BARU"] + df["id_tanaman"].tolist()

    st.subheader("➕ ✏ 🗑 Form Tambah / Edit / Hapus")
    with st.form("crud_form"):
        pilih = st.selectbox("🆔 Pilih ID Tanaman", ids)

        if pilih != "BARU":
            row = df[df["id_tanaman"] == pilih].iloc[0]
            nama = st.text_input("🌱 Nama Tanaman", row["nama_tanaman"])
            frek = st.text_input("💧 Frekuensi Siram", row["frekuensi_siram"])
            pupuk = st.text_input("🧪 Jenis Pupuk", row["jenis_pupuk"])
            tanggal = st.date_input("📅 Tanggal Siram Terakhir", pd.to_datetime(row["tanggal_siram_terakhir"]))
            cat = st.text_area("📝 Catatan", row["catatan"])
        else:
            nama = st.text_input("🌱 Nama Tanaman")
            frek = st.text_input("💧 Frekuensi Siram")
            pupuk = st.text_input("🧪 Jenis Pupuk")
            tanggal = st.date_input("📅 Tanggal Siram Terakhir")
            cat = st.text_area("📝 Catatan")

        col1, col2, col3 = st.columns(3)
        tambah = col1.form_submit_button("➕ Tambah")
        update = col2.form_submit_button("✏ Update")
        hapus = col3.form_submit_button("🗑 Hapus")

    if tambah and pilih == "BARU" and nama:
        nid = add_plant(nama, frek, pupuk, tanggal.strftime("%Y-%m-%d"), cat)
        st.success(f"✅ Data ditambahkan (ID: {nid})")

    if update and pilih != "BARU":
        update_plant(pilih, {
            "nama_tanaman": nama,
            "frekuensi_siram": frek,
            "jenis_pupuk": pupuk,
            "tanggal_siram_terakhir": tanggal.strftime("%Y-%m-%d"),
            "catatan": cat
        })
        st.success("✏ Data berhasil diupdate")

    if hapus and pilih != "BARU":
        delete_plant(pilih)
        st.warning("🗑 Data dihapus")

    st.markdown("---")
    st.subheader("📄 Tabel Data Tanaman")
    df_show = load_data()
    df_show.index = df_show.index + 1
    st.dataframe(df_show, use_container_width=True)

# ================= GENERATE QR =================
elif menu == "🔖 Generate QR":
    st.title("🔖 Generate QR Code 🌿")

    df = load_data()
    pilih = st.multiselect("🆔 Pilih ID Tanaman", df["id_tanaman"].tolist())

    if st.button("📦 Generate QR"):
        targets = df["id_tanaman"].tolist() if not pilih else pilih
        for tid in targets:
            img = generate_qr(tid)
            st.image(img, width=160, caption=f"QR ID: {tid}")

# ================= SCAN QR =================
elif menu == "📷 Scan QR / Input Manual":
    st.title("📷 Scan QR Tanaman (400×400)")

    cam = st.camera_input("📸 Arahkan QR ke kamera")
    detector = cv2.QRCodeDetector()
    id_found = None

    if cam:
        img = Image.open(cam)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        data, _, _ = detector.detectAndDecode(img_np)

        if data:
            id_found = data
            st.success(f"✅ QR Terbaca: {data}")
        else:
            st.error("❌ QR tidak terbaca")

    st.markdown("---")
    manual = st.text_input("✍ Atau masukkan ID manual")
    tid = id_found or manual.strip()

    if tid:
        plant = get_plant(tid)
        if plant:
            st.write(plant)
            if st.button("💧 Tambah catatan penyiraman"):
                add_note(tid, "Disiram via scan")
                st.success("📝 Catatan ditambahkan")
        else:
            st.error("❌ ID tidak ditemukan")

# ================= GRAFIK =================
elif menu == "📊 Grafik / Laporan":
    st.title("📊 Grafik & Laporan 📈")
    df = load_data()
    st.dataframe(df, use_container_width=True)
    
    # --- BAGIAN GRAFIK DIGANTI KE PLOTLY ---
    if not df.empty:
        # Menghitung jumlah per jenis pupuk
        data_grafik = df['jenis_pupuk'].value_counts().reset_index()
        data_grafik.columns = ['Jenis Pupuk', 'Jumlah']
        
        st.subheader("Statistik Pupuk")
        fig = px.bar(
            data_grafik, 
            x='Jenis Pupuk', 
            y='Jumlah',
            title='Distribusi Penggunaan Pupuk',
            text='Jumlah',
            color='Jenis Pupuk',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig, use_container_width=True)

# ================= TENTANG =================
elif menu == "ℹ Tentang":
    st.title("ℹ Tentang Aplikasi 🌱")
    st.markdown("""
    *🌿 Sistem Catatan Perawatan Tanaman Hias*  

    ✅ CRUD berbasis CSV  
    ✅ Generate QR Code  
    ✅ Scan QR via Kamera (OpenCV)  
    ✅ Grafik & Laporan (Interactive Plotly)
    ✅ Mode Offline  
    ✅ Tema Hijau Tanaman Hias 🌱  
    """)