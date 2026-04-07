import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import base64
import time 

# --- CONFIG ---
st.set_page_config(page_title="Form UDIKSAR CKG PUSKESMAS", layout="centered")

# --- INITIALIZE SESSION STATE ---
if 'form_idx' not in st.session_state:
    st.session_state.form_idx = 0

def reset_form():
    st.session_state.form_idx += 1

# --- FUNGSI POP-UP DUPLIKAT ---
@st.dialog("⚠️ DATA SUDAH TERDAFTAR")
def show_duplicate_popup(nama, nik):
    st.warning(f"Halo, data dengan NIK **{nik}** atas nama **{nama}** sudah ada di sistem kami.")
    st.info("Formulir akan dikosongkan kembali agar bisa digunakan untuk pengisian data berikutnya.")
    if st.button("SAYA MENGERTI (KOSONGKAN FORM)", use_container_width=True):
        reset_form()
        st.rerun()

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
                background-color: rgba(0, 0, 0, 0.75);
                padding: 30px !important;
                border-radius: 20px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
                color: white;
                margin-top: 20px;
            }}

            h1 {{
                color: white !important;
                text-align: center;
                background-color: rgba(0, 128, 0, 0.8);
                padding: 15px;
                border-radius: 12px;
                font-size: 20px !important;
            }}

            h3 {{
                color: #25D366 !important;
                border-bottom: 2px solid #25D366;
                margin-top: 20px;
            }}

            /* Styling Tombol Simpan (Merah) */
            div.stButton > button:first-child {{
                background-color: #FF4B4B;
                color: white;
                border: none;
                height: 45px;
                width: 100%;
                font-weight: bold;
                border-radius: 10px;
            }}
            
            div.stButton > button:hover {{
                background-color: #FF2B2B;
                border: none;
                color: white;
            }}

            /* Styling Tombol WA (Hijau) */
            .btn-wa {{
                background-color: #25D366;
                color: white !important;
                border-radius: 10px;
                text-decoration: none;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                height: 45px;
                width: 100%;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .btn-wa:hover {{ background-color: #128C7E; }}

            /* Responsif untuk HP */
            @media (max-width: 640px) {{
                [data-testid="column"] {{
                    width: 100% !important;
                    flex: 1 1 100% !important;
                    margin-bottom: 10px;
                }}
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

st.markdown("<h1>🏥 CKG SEKOLAH PUSKESMAS PWT SELATAN</h1>", unsafe_allow_html=True)

# Data Sekolah (Kunci dirubah dari SD jadi SD/MI)
data_sekolah = {
    "SD/MI": {
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
        "PWT KULON": ["SMP MUHAMMAYDIYAH 1 PURWOKERTO", "SMP 3 BAHASA PUTERA HARAPAN"],
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
f_key = st.session_state.form_idx

st.subheader("Data Identitas")
nama_lengkap = st.text_input("Nama Lengkap", placeholder="Contoh: ADZRIEL ...", key=f"nama_{f_key}")
nik = st.text_input("NIK (16 Digit)", placeholder="Masukkan 16 digit NIK", key=f"nik_{f_key}")

col1, col2 = st.columns(2)
with col1:
    tgl_lahir = st.date_input("Tanggal Lahir", min_value=datetime(2000, 1, 1), value=None, key=f"tgl_{f_key}")
    gender = st.selectbox("Jenis Kelamin", ["-- Pilih --", "Laki-laki", "Perempuan"], index=0, key=f"gen_{f_key}")
with col2:
    wa = st.text_input("No. WhatsApp", placeholder="Contoh: 08123456789", key=f"wa_{f_key}")
    disabilitas = st.selectbox("Disabilitas", ["Tidak", "Netra", "Rungu", "Daksa", "Grahita", "Lainnya"], key=f"dis_{f_key}")

st.subheader("Data Pendidikan")
jenjang_input = st.selectbox("Jenjang Pendidikan", ["-- Pilih Jenjang --", "SD/MI", "SMP", "SMA/SMK"], index=0, key=f"jen_{f_key}")

angka_kelas = "-- Pilih --"
kelurahan_sekolah = "-- Pilih --"
sekolah_terpilih = "-- Pilih --"

if jenjang_input != "-- Pilih Jenjang --":
    list_kelas = ["1", "2", "3", "4", "5", "6"] if jenjang_input == "SD/MI" else (["7", "8", "9"] if jenjang_input == "SMP" else ["10", "11", "12"])
    col_edu1, col_edu2 = st.columns(2)
    with col_edu1:
        angka_kelas = st.selectbox("Pilih Kelas", ["-- Pilih Kelas --"] + list_kelas, key=f"kls_{f_key}")
    with col_edu2:
        list_kel = ["-- Pilih Kelurahan --"] + list(data_sekolah[jenjang_input].keys())
        kelurahan_sekolah = st.selectbox("Kelurahan Sekolah", list_kel, key=f"kel_{f_key}")

    if kelurahan_sekolah != "-- Pilih Kelurahan --":
        sekolah_terpilih = st.selectbox("Nama Sekolah", ["-- Pilih Sekolah --"] + data_sekolah[jenjang_input][kelurahan_sekolah], key=f"sch_{f_key}")

st.subheader("Data Domisili")
alamat_domisili = st.text_input("Alamat Domisili (RT/RW)", placeholder="Contoh: RT 02 / RW 01", key=f"dom_{f_key}")
detail_alamat = st.text_area("Detail Alamat (Nama Jalan/Blok)", key=f"det_{f_key}")

c1, c2, c3 = st.columns(3)
with c1: kec = st.text_input("Kecamatan", value="Purwokerto Selatan", key=f"kec_{f_key}")
with c2: kab = st.text_input("Kabupaten", value="Banyumas", key=f"kab_{f_key}")
with c3: prov = st.text_input("Propinsi", value="Jawa Tengah", key=f"prov_{f_key}")

st.markdown("<br>", unsafe_allow_html=True)

# --- TOMBOL ---
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    submit = st.button("SIMPAN DATA", type="primary", use_container_width=True)
with col_btn2:
    st.markdown(f"""<a href="https://wa.me/6289665803467" target="_blank" class="btn-wa">💬 CONTACT US (WA)</a>""", unsafe_allow_html=True)

# --- LOGIKA PENYIMPANAN + ANTI DUPLIKAT ---
if submit:
    invalid_values = [None, "", "-- Pilih --", "-- Pilih Jenjang --", "-- Pilih Kelas --", "-- Pilih Kelurahan --", "-- Pilih Sekolah --"]
    
    if any(x in invalid_values for x in [nama_lengkap, nik, wa, alamat_domisili, jenjang_input, angka_kelas, kelurahan_sekolah, sekolah_terpilih, gender]):
        st.error("❌ Mohon lengkapi semua data wajib!")
    elif len(nik) != 16 or not nik.isdigit():
        st.error("❌ NIK harus berjumlah 16 digit angka!")
    else:
        try:
            with st.spinner("Sedang mengecek data..."):
                df_lama = conn.read(worksheet="MASTER_DATA", ttl=0)
                nik_list = df_lama['nik'].astype(str).str.replace("'", "").tolist()
                
                if nik in nik_list:
                    data_exist = df_lama[df_lama['nik'].astype(str).str.contains(nik)]
                    nama_sudah_ada = data_exist['nama_lengkap'].values[0] if not data_exist.empty else "User"
                    show_duplicate_popup(nama_sudah_ada, nik)
                else:
                    new_data = {
                        "nik": f"'{nik}",
                        "nama_lengkap": str(nama_lengkap).upper(),
                        "tanggal_lahir": str(tgl_lahir),
                        "jenis_kelamin": str(gender),
                        "no_whatsapp": f"'{wa}",
                        "status_pernikahan": "Belum Menikah",
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
                    reset_form()
                    st.rerun()

        except Exception as e:
            st.error(f"⚠️ Terjadi Kesalahan: {e}")
