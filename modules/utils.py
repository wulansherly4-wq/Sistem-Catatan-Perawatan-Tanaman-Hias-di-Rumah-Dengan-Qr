# utils.py
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# ===== KONFIGURASI FILE =====
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "tanaman.csv")
LOG_FILE = os.path.join(DATA_DIR, "log.csv")

# =====================================================
# 1. Pastikan folder & file tersedia
# =====================================================
def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs("qr", exist_ok=True)

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "id_tanaman",
            "nama_tanaman",
            "frekuensi_siram",
            "jenis_pupuk",
            "tanggal_siram_terakhir",
            "catatan"
        ])
        df.to_csv(DATA_FILE, index=False)

    if not os.path.exists(LOG_FILE):
        log_df = pd.DataFrame(columns=[
            "timestamp",
            "id_tanaman",
            "aksi",
            "keterangan"
        ])
        log_df.to_csv(LOG_FILE, index=False)

# =====================================================
# 2. Load data tanaman (READ)
# =====================================================
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except Exception:
        ensure_data_files()
        return pd.read_csv(DATA_FILE)

# =====================================================
# 3. Simpan data tanaman (SAVE)
# =====================================================
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# =====================================================
# 4. Generate ID otomatis (T001, T002, ...)
# =====================================================
def generate_new_id():
    df = load_data()
    existing = df["id_tanaman"].dropna().tolist()
    nums = [int(x[1:]) for x in existing if isinstance(x, str) and x.startswith("T")]
    n = max(nums) + 1 if nums else 1
    return f"T{n:03d}"

# =====================================================
# 5. CREATE (Tambah Tanaman)
# =====================================================
def add_plant(nama, frekuensi, pupuk, tanggal, catatan=""):
    df = load_data()
    nid = generate_new_id()

    row = {
        "id_tanaman": nid,
        "nama_tanaman": nama,
        "frekuensi_siram": frekuensi,
        "jenis_pupuk": pupuk,
        "tanggal_siram_terakhir": tanggal,
        "catatan": catatan
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df)

    log_action(nid, "CREATE", f"Tambah tanaman {nama}")
    return nid

# =====================================================
# 6. READ by ID
# =====================================================
def get_plant(id_tanaman):
    df = load_data()
    row = df[df["id_tanaman"] == id_tanaman]
    return row.iloc[0].to_dict() if not row.empty else None

# =====================================================
# 7. UPDATE
# =====================================================
def update_plant(id_tanaman, updates: dict):
    df = load_data()
    for k, v in updates.items():
        if k in df.columns:
            df.loc[df["id_tanaman"] == id_tanaman, k] = v
    save_data(df)

    log_action(id_tanaman, "UPDATE", "Update data tanaman")

# =====================================================
# 8. DELETE
# =====================================================
def delete_plant(id_tanaman):
    df = load_data()
    df = df[df["id_tanaman"] != id_tanaman]
    save_data(df)

    log_action(id_tanaman, "DELETE", f"Hapus data {id_tanaman}")

# =====================================================
# 9. Tambah Catatan Penyiraman
# =====================================================
def add_note(id_tanaman, teks):
    df = load_data()
    mask = df["id_tanaman"] == id_tanaman

    if mask.any():
        prev = str(df.loc[mask, "catatan"].iloc[0])
        new_note = f"{prev} | {teks}" if prev and prev != "nan" else teks

        df.loc[mask, "catatan"] = new_note
        df.loc[mask, "tanggal_siram_terakhir"] = datetime.now().strftime("%Y-%m-%d")

        save_data(df)
        log_action(id_tanaman, "NOTE", teks)
        return True

    return False

# =====================================================
# 10. Grafik Matplotlib (opsional / legacy)
# =====================================================
def create_chart():
    df = load_data()
    if df.empty:
        return None

    grp = df["jenis_pupuk"].fillna("(kosong)").value_counts()

    fig, ax = plt.subplots()
    grp.plot(kind="bar", ax=ax)
    ax.set_title("Jumlah Tanaman per Jenis Pupuk")
    ax.set_ylabel("Jumlah")
    fig.tight_layout()

    return fig

# =====================================================
# 11. LOG HARIAN (INTI BAB 5.3)
# =====================================================
def log_action(id_tanaman, aksi, keterangan=""):
    ensure_data_files()

    try:
        logs = pd.read_csv(LOG_FILE)
    except Exception:
        logs = pd.DataFrame(columns=["timestamp", "id_tanaman", "aksi", "keterangan"])

    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id_tanaman": id_tanaman,
        "aksi": aksi,
        "keterangan": keterangan
    }

    logs = pd.concat([logs, pd.DataFrame([new_log])], ignore_index=True)
    logs.to_csv(LOG_FILE, index=False)

def load_log():
    ensure_data_files()
    return pd.read_csv(LOG_FILE)

# =====================================================
# 12. Export ke Excel
# =====================================================
def export_to_excel(path="data/export.xlsx"):
    df = load_data()
    df.to_excel(path, index=False)
    return path
