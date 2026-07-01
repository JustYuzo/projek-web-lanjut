import google.generativeai as genai
import json
import os

# Konfigurasi Gemini
# Pastikan Anda sudah punya API KEY dari Google AI Studio (gratis)
genai.configure(api_key="ISI_API_KEY_ANDA_DI_SINI")

def analyze_image_with_ai(image_path, tipe_analisis="pembayaran"):
    """
    tipe_analisis: 'pembayaran' atau 'dokumen'
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Membaca file gambar
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    prompt = ""
    if tipe_analisis == "pembayaran":
        prompt = """
        Analisis bukti transfer ini. Kembalikan dalam format JSON murni tanpa markdown:
        {
            "nominal": int,
            "status": "jelas" | "buram" | "tidak_valid",
            "catatan": "penjelasan singkat"
        }
        """
    else: # Dokumen (KTP/SIM)
        prompt = """
        Analisis dokumen ini. Apakah ini KTP atau SIM? Apakah jelas atau buram? 
        Kembalikan dalam format JSON murni tanpa markdown:
        {
            "jenis": "ktp" | "sim" | "lainnya",
            "status": "jelas" | "buram" | "tidak_valid",
            "catatan": "penjelasan singkat"
        }
        """

    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": image_data}
    ])
    
    # Membersihkan response agar jadi JSON murni
    text_response = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(text_response)