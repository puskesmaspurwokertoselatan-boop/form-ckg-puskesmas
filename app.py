import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import base64
import time 

# --- CONFIG ---
st.set_page_config(page_title="Form UDIKSAR CKG PUSKESMAS", layout="centered")

# --- FUNGSI BACKGROUND & STYLING ---
def set_bg_and_style(main_bg_img):
    try:
        with open(main_bg_img, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            header {{visibility: hidden;}}
            [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
            footer {{visibility: hidden;}}

            .stApp {{
                background: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center 90%; 
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            
            .stMainBlockContainer {{
                background-color: rgba(0, 0, 0, 0.69);
                padding: 40px !important;
                border-radius: 20px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
                color: white;
                margin-top: 30px;
                margin-bottom: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            [data-testid="stWidgetLabel"] p {{ 
                color: white !important; 
                font-weight: bold; 
                font-size: 1rem;
            }}

            h1 {{
                color: white !important;
                text-shadow: 2px 2px 10px #000000;
                text-align: center;
                background-color: rgba(0, 128, 0, 0.8);
                padding: 18px;
                border-radius: 12px;
                margin-bottom: 25px;
                font-size: 22px !important;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}

            h3 {{
                color: #25D366 !important;
                border-bottom: 2px solid #25D366;
                padding-bottom: 5px;
                margin-top: 20px;
            }}

            [data-testid="column"] {{
                display: flex;
                align-items: flex-end;
            }}

            .btn-wa {{
                background-color: #25D366;
                color: white !important;
                border-radius: 0.5rem;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: 400;
                font-size: 1rem;
                height: 38.4px; 
                width: 100%;
                transition: 0.3s;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-sizing: border-box;
                line-height: 1.6;
                padding: 0px 16px;
            }}
            .btn-wa:hover {{ 
                background-color: #128C7E; 
                color: white !important;
                border-color: #25D366;
            }}

            .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTextArea textarea {{
                border: 1px solid #ccc !important;
                box-shadow: none !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

set_bg_and_style("IMG_20260402_084603.jpg")

conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("<h1>🏥 CKG SEKOLAH PUSKESMAS PWT SELATAN</h1>", unsafe_allow_html=True)

# Data Sekolah
data_sekolah = {
    "SD": {
        "KARANGKLESEM": ["Sekolah Dasar Negeri 1 Karangklesem Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Karangklesem Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 4 Karangklesem Kecamatan Purwokerto Selatan", "MIS DIPONEGORO 03 KARANGKLESEM", "SD IT HARAPAN BUNDA", "SD IT AZ-AZAHRA", "SD ISLAM BINA INSAN MANDIRI PURWOKERTO"],
        "TELUK": ["Sekolah Dasar Negeri 1 Teluk Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Teluk Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 4 Teluk Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 5 Teluk Kecamatan Purwokerto Selatan", "MIS MA`ARIF NU TELUK"],
        "BERKOH": ["Sekolah Dasar Negeri 1 Berkoh Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 2 Berkoh Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Berkoh Kecamatan Purwokerto Selatan"],
        "PWT KIDUL": ["Sekolah Dasar Negeri 1 Purwokerto Kidul Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Purwokerto Kidul Kecamatan Purwokerto Selatan", "SD PALM KIDS PURWOKERTO", "PKBM TERANG MULIA"],
        "PWT KULON": ["Sekolah Dasar Negeri 1 Purwokerto Kulon Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 2 Purwokerto Kulon Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Purwokerto Kulon Kecamatan Purwokerto Selatan", "SD 3 BAHASA PUTERA HARAPAN"],
        "TANJUNG": ["Sekolah Dasar Negeri 1 Tanjung Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 2 Tanjung Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Tanjung Kecamatan Purwokerto Selatan", "SD MUHAMMADIYAH Tanjung", "SDIT MUTIARA HATI", "SLB C DAN C1 YAKUT PURWOKERTO"],
        "KARANG PUCUNG": ["Sekolah Dasar Negeri 1 Karangpucung Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 4 Karangpucung Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 5 Karangpucung Kecamatan Purwokerto Selatan", "MIS AL-IKHLAS KARANGPUCUNG", "MIS MA`ARIF NU KARANGPUCUNG"]
    },
    "SMP": {
        "KARANGKLESEM": ["Sekolah Menengah Pertama Negeri 5 Purwokerto"],
        "TELUK": ["Sekolah Menengah Pertama Negeri 7 Purwokerto", "SMP ISLAM TERPADU HARAPAN BUNDA", "SMP MAARIF NU 03 PURWOKERTO"],
        "BERKOH": ["SMP DIPONEGORO 1 PURWOKERTO"],
        "PWT KIDUL": ["SMP TELKOM PURWOKERTO", "SMP MAARIF NU 2 PURWOKERTO", "PKBM TERANG MULIA"],
        "PWT KULON": ["SMP MUHAMMADIYAH 1 PURWOKERTO", "SMP 3 BAHASA PUTERA HARAPAN"],
        "TANJUNG": ["SMP MUHAMMADIYAH 2 PURWOKERTO", "SLB C DAN C1 YAKUT PURWOKERTO"],
        "KARANG PUCUNG": ["-"]
    },
    "SMA/SMK": {
        "KARANGKLESEM": ["SMK SWAGAYA 2 PURWOKERTO", "SMK MUHAMMADIYAH 3 PURWOKERTO", "SMK NASIONAL PURWOKERTO"],
        "TELUK": ["SMK MA`ARIF NU 1 PURWOKERTO"],
        "BERKOH": ["SMK DIPONEGORO 1 PURWOKERTO", "SMAS JENDERAL SUDIRMAN PWT"],
        "PWT KIDUL": ["SMK TELKOM PURWOKERTO"],
        "PWT KULON": ["SMA 3 BAHASA PUTERA HARAPAN"],
        "TANJUNG": ["SMK BINA TEKNOLOGI PURWOKERTO", "SMK CITRA BANGSA MANDIRI PURWOKERTO", "SMK TUJUH LIMA 1 PURWOKERTO", "SMK TUJUH LIMA 2 PURWOKERTO", "SLB C DAN C1 YAKUT PURWOKERTO"],
        "KARANG PUCUNG": ["SMK TEKNOLOGI NASIONAL PURWOKERTO"]
    }
}

# --- FORM RESET LOGIC ---
# Kita gunakan container form agar bisa reset otomatis
with st.form("udiksar_form", clear_on_submit=True):
    st.subheader("Data Identitas")
    nama_lengkap = st.text_input("Nama Lengkap", placeholder="Contoh: ADZRIEL ...")
    nik = st.text_input("NIK (16 Digit)", placeholder="Masukkan 16 digit NIK")

    col1, col2 = st.columns(2)
    with col1:
        tgl_lahir = st.date_input("Tanggal Lahir", min_value=datetime(2000, 1, 1), value=None)
        gender = st.selectbox("Jenis Kelamin", ["-- Pilih --", "Laki-laki", "Perempuan"])
    with col2:
        wa = st.text_input("No. WhatsApp", placeholder="Contoh: 08123456789")
        disabilitas = st.selectbox("Disabilitas", ["Tidak", "Netra", "Rungu", "Daksa", "Grahita", "Lainnya"])

    status_nikah_default = "Belum Menikah"

    st.subheader("Data Pendidikan")
    jenjang_input = st.selectbox("Jenjang Pendidikan", ["-- Pilih Jenjang --", "SD", "SMP", "SMA/SMK"])

    # Placeholder untuk data pendidikan yang dinamis
    angka_kelas = "-- Pilih --"
    kelurahan_sekolah = "-- Pilih --"
    sekolah_terpilih = "-- Pilih --"

    if jenjang_input != "-- Pilih Jenjang --":
        list_kelas = ["1", "2", "3", "4", "5", "6"] if jenjang_input == "SD" else (["7", "8", "9"] if jenjang_input == "SMP" else ["10", "11", "12"])
        col_edu1, col_edu2 = st.columns(2)
        with col_edu1:
            angka_kelas = st.selectbox("Pilih Kelas", ["-- Pilih Kelas --"] + list_kelas)
        with col_edu2:
            list_kel = ["-- Pilih Kelurahan --"] + list(data_sekolah[jenjang_input].keys())
            kelurahan_sekolah = st.selectbox("Kelurahan Sekolah", list_kel)
        
        if kelurahan_sekolah != "-- Pilih Kelurahan --":
            sekolah_terpilih = st.selectbox("Nama Sekolah", ["-- Pilih Sekolah --"] + data_sekolah[jenjang_input][kelurahan_sekolah])

    st.subheader("Data Domisili")
    alamat_domisili = st.text_input("Alamat Domisili (RT/RW)", placeholder="Contoh: RT 02 / RW 01")
    detail_alamat = st.text_area("Detail Alamat (Nama Jalan/Blok)")

    c1, c2, c3 = st.columns(3)
    with c1: kec = st.text_input("Kecamatan", value="Purwokerto Selatan")
    with c2: kab = st.text_input("Kabupaten", value="Banyumas")
    with c3: prov = st.text_input("Propinsi", value="Jawa Tengah")

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        submit = st.form_submit_button("SIMPAN DATA", use_container_width=True)
    with col_btn2:
        # Tombol WA ditaruh di luar form submit agar tidak memicu pengiriman data
        pass

# Tombol WA di luar form agar tetap berfungsi sebagai link
if not submit:
    st.markdown(f"""<a href="https://wa.me/6289665803467" target="_blank" class="btn-wa" style="margin-top:-95px; position:relative; z-index:999;">💬 CONTACT US (WA)</a>""", unsafe_allow_html=True)

# --- LOGIKA PENYIMPANAN ---
if submit:
    invalid_values = [None, "", "-- Pilih --", "-- Pilih Jenjang --", "-- Pilih Kelas --", "-- Pilih Kelurahan --", "-- Pilih Sekolah --"]
    
    if any(x in invalid_values for x in [nama_lengkap, nik, wa, alamat_domisili, jenjang_input, angka_kelas, kelurahan_sekolah, sekolah_terpilih, gender]):
        st.error("❌ Mohon lengkapi semua data wajib!")
        time.sleep(2)
        st.rerun()
    elif len(nik) != 16 or not nik.isdigit():
        st.error("❌ NIK harus berjumlah 16 digit angka!")
        time.sleep(2)
        st.rerun()
    else:
        try:
            with st.spinner("Sedang memproses..."):
                df_lama = conn.read(worksheet="MASTER_DATA", ttl=0)
                new_data = {
                    "nik": f"'{nik}",
                    "nama_lengkap": str(nama_lengkap).upper(),
                    "tanggal_lahir": str(tgl_lahir),
                    "jenis_kelamin": str(gender),
                    "no_whatsapp": f"'{wa}",
                    "status_pernikahan": status_nikah_default,
                    "disabilitas": str(disabilitas),
                    "nama_sekolah": str(sekolah_terpilih),
                    "jenjang_pendidikan": f"KELAS {angka_kelas}", 
                    "alamat_domisili": str(alamat_domisili),
                    "detail_alamat": str(detail_alamat),
                    "alamat_sama_sekolah": "Ya",
                    "Propinsi": str(prov),
                    "kabupaten": str(kab),
                    "kecamatan": str(kec),
                    "Kelurahan": str(kelurahan_sekolah),
                    "ID_TRANSAKSI": str(uuid.uuid4())[:8].upper(),
                    "TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                updated_df = pd.concat([df_lama, pd.DataFrame([new_data])], ignore_index=True)
                conn.update(worksheet="MASTER_DATA", data=updated_df)
                
                st.success(f"✅ Data {nama_lengkap} Berhasil Tersimpan!")
                st.balloons()
                
                time.sleep(2)
                st.rerun() # Ini akan merefresh halaman dan karena clear_on_submit=True, form jadi kosong bersih

        except Exception as e:
            st.error(f"⚠️ Terjadi Kesalahan: {e}")
