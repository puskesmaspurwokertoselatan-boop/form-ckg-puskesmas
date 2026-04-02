import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import base64

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
                background-color: rgba(0, 128, 0, 0.7);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 25px;
            }}

            h3 {{
                color: #25D366 !important;
                border-bottom: 2px solid #25D366;
                padding-bottom: 5px;
                margin-top: 20px;
            }}

            /* Menyejajarkan tombol Simpan dan WhatsApp */
            [data-testid="column"] {{
                display: flex;
                align-items: flex-end;
            }}

            /* Perbaikan Tombol WA agar identik dengan tombol Streamlit */
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
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

set_bg_and_style("IMG_20260402_084603.jpg")

# --- KONEKSI GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏥 CKG SEKOLAH PUSKESMAS PURWOKERTO SELATAN")

# Data Sekolah (Tetap sama)
data_sekolah = {
    "SD": {
        "KARANGKLESEM": ["Sekolah Dasar Negeri 1 Karangklesem Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Karangklesem Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 4 Karangklesem Kecamatan Purwokerto Selatan", "MIS DIPONEGORO 03 KARANGKLESEM", "SD IT HARAPAN BUNDA", "SD IT AZ-AZAHRA", "SD ISLAM BINA INSAN MANDIRI PURWOKERTO"],
        "TELUK": ["Sekolah Dasar Negeri 1 Teluk Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Teluk Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 4 Teluk Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 5 Teluk Kecamatan Purwokerto Selatan", "MIS MA`ARIF NU TELUK"],
        "BERKOH": ["Sekolah Dasar Negeri 1 Berkoh Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 2 Berkoh Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Berkoh Kecamatan Purwokerto Selatan"],
        "PWT KIDUL": ["Sekolah Dasar Negeri 1 Purwokerto Kidul Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Purwokerto Kidul Kecamatan Purwokerto Selatan", "SD PALM KIDS PURWOKERTO", "PKBM TERANG MULIA"],
        "PWT KULON": ["Sekolah Dasar Negeri 1 Purwokerto Kulon Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 2 Purwokerto Kulon Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Purwokerto Kulon Kecamatan Purwokerto Selatan", "SD 3 BAHASA PUTERA HARAPAN"],
        "TANJUNG": ["Sekolah Dasar Negeri 1 Tanjung Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 2 Tanjung Kecamatan Purwokerto Selatan", "Sekolah Dasar Negeri 3 Tanjung Kecamatan Purwokerto Selatan", "SD MUHAMMADIYAH TANJUNG", "SDIT MUTIARA HATI", "SLB C DAN C1 YAKUT PURWOKERTO"],
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

# --- BAGIAN FORM ---
st.subheader("Data Identitas")
nama_lengkap = st.text_input("Nama Lengkap", placeholder="Contoh: ADZRIEL ...")
nik = st.text_input("NIK (16 Digit)", placeholder="Masukkan 16 digit NIK")

col1, col2 = st.columns(2)
with col1:
    tgl_lahir = st.date_input("Tanggal Lahir", min_value=datetime(2000, 1, 1), value=None)
    gender = st.selectbox("Jenis Kelamin", ["-- Pilih --", "Laki-laki", "Perempuan"], index=0)
with col2:
    wa = st.text_input("No. WhatsApp", placeholder="Contoh: 08123456789")
    disabilitas = st.selectbox("Disabilitas", ["Tidak", "Netra", "Rungu", "Daksa", "Grahita", "Lainnya"])

status_nikah = st.selectbox("Status Pernikahan", ["Belum Kawin", "Kawin"])

st.subheader("Data Pendidikan")
jenjang_input = st.selectbox("Jenjang Pendidikan", ["-- Pilih Jenjang --", "SD", "SMP", "SMA/SMK"], index=0)

angka_kelas = "-- Pilih --"
kelurahan_sekolah = "-- Pilih --"
sekolah_terpilih = "-- Pilih --"

if jenjang_input != "-- Pilih Jenjang --":
    if jenjang_input == "SD":
        list_kelas = ["1", "2", "3", "4", "5", "6"]
    elif jenjang_input == "SMP":
        list_kelas = ["7", "8", "9"]
    else:
        list_kelas = ["10", "11", "12"]

    col_edu1, col_edu2 = st.columns(2)
    with col_edu1:
        angka_kelas = st.selectbox("Pilih Kelas", ["-- Pilih Kelas --"] + list_kelas, key=f"kelas_{jenjang_input}")
    with col_edu2:
        list_kel = ["-- Pilih Kelurahan --"] + list(data_sekolah[jenjang_input].keys())
        kelurahan_sekolah = st.selectbox("Kelurahan Sekolah", list_kel, key=f"kel_{jenjang_input}")

    if kelurahan_sekolah != "-- Pilih Kelurahan --":
        sekolah_terpilih = st.selectbox("Nama Sekolah", ["-- Pilih Sekolah --"] + data_sekolah[jenjang_input][kelurahan_sekolah], key=f"sch_{jenjang_input}_{kelurahan_sekolah}")
else:
    st.info("Silakan tentukan Jenjang Pendidikan terlebih dahulu.")

st.subheader("Data Domisili")
alamat_domisili = st.text_input("Alamat Domisili (RT/RW)", placeholder="Contoh: RT 02 / RW 01")
detail_alamat = st.text_area("Detail Alamat (Nama Jalan/Blok)")

c1, c2, c3 = st.columns(3)
with c1: kec = st.text_input("Kecamatan", value="Purwokerto Selatan")
with c2: kab = st.text_input("Kabupaten", value="Banyumas")
with c3: prov = st.text_input("Propinsi", value="Jawa Tengah")

st.markdown("<br>", unsafe_allow_html=True)

# SEJAJARKAN TOMBOL
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    submit = st.button("SIMPAN DATA", type="primary", use_container_width=True)
with col_btn2:
    st.markdown(f"""<a href="https://wa.me/6289665803467" target="_blank" class="btn-wa">💬 CONTACT US (WA)</a>""", unsafe_allow_html=True)

# --- LOGIKA PENYIMPANAN ---
if submit:
    invalid_values = [None, "", "-- Pilih --", "-- Pilih Jenjang --", "-- Pilih Kelas --", "-- Pilih Kelurahan --", "-- Pilih Sekolah --"]
    
    if any(x in invalid_values for x in [nama_lengkap, nik, wa, alamat_domisili, jenjang_input, angka_kelas, kelurahan_sekolah, sekolah_terpilih, gender]):
        st.error("❌ Mohon lengkapi semua data wajib (termasuk NIK)!")
    elif len(nik) != 16 or not nik.isdigit():
        st.error("❌ NIK harus berjumlah 16 digit angka!")
    else:
        try:
            with st.spinner("Sedang memproses..."):
                df_lama = conn.read(worksheet="MASTER_DATA", ttl=0)
                new_data = {
                    "nama_lengkap": str(nama_lengkap).upper(),
                    "nik": f"'{nik}", # Menggunakan tanda kutip agar tidak dianggap angka scientific di Excel
                    "tanggal_lahir": str(tgl_lahir),
                    "jenis_kelamin": str(gender),
                    "no_whatsapp": f"'{wa}",
                    "status_pernikahan": str(status_nikah),
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
        except Exception as e:
            st.error(f"⚠️ Terjadi Kesalahan: {e}")
