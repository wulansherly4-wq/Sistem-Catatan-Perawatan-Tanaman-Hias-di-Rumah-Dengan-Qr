# qr_utils.py
import os
import qrcode
from PIL import Image
from io import BytesIO

# 1 fungsi: generate QR (simpan di folder /qr)
def generate_qr(id_tanaman, save_folder="qr"):
    os.makedirs(save_folder, exist_ok=True)
    img = qrcode.make(id_tanaman)
    path = os.path.join(save_folder, f"{id_tanaman}.png")
    img.save(path)
    return path

# helper: try decode using pyzbar if tersedia
def try_decode_image_bytes(file_bytes):
    try:
        from pyzbar.pyzbar import decode
    except Exception:
        return None  # pyzbar tidak terpasang
    try:
        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        decoded = decode(img)
        if decoded:
            return decoded[0].data.decode("utf-8")
        return None
    except Exception:
        return None
