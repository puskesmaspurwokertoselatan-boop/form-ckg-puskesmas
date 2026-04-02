import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import base64 # Diperlukan untuk membaca file lokal

# --- CONFIG ---
st.set_page_config(page_title="Form UDIKSAR CKG PUSKESMAS", layout="centered")

# --- FUNGSI BACKGROUND LAYAR PENUH ---
def set_bg_local(main_bg_img):
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
            
            @media (max-width: 768px) {{
                .stApp {{
                    background-attachment: scroll;
                    background-position: center 90%;
                }}
                [data-testid="stForm"] {{
                    padding: 15px;
                }}
            }}

            [data-testid="stForm"] {{
                background-color: rgba(0, 0, 0, 0.7);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
                color: white;
            }}
            
            [data-testid="stWidgetLabel"] p {{
                color: white !important;
                font-weight: bold;
            }}

            h1 {{
                color: white !important;
                text-shadow: 2px 2px 10px #000000;
                text-align: center;
                background-color: rgba(0, 128, 0, 0.6);
                padding: 15px;
                border-radius: 10px;
            }}

            .btn-wa {{
                background-color: #25D366;
                color: white !important;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                text-decoration: none;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                height: 45px;
                border: none;
                transition: 0.3s;
            }}
            .btn-wa:hover {{
                background-color: #128C7E;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"⚠️ File '{main_bg_img}' tidak ditemukan.")

# PANGGIL FOTO
set_bg_local("IMG_20260402_084603.jpg")

# Data Sekolah Formal
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

# --- KONEKSI GSHEETS ---
# Koneksi otomatis membaca dari .streamlit/secrets.toml atau Secrets di Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏥 CKG SEKOLAH PUSKESMAS PURWOKERTO SELATAN")
st.markdown("---")

with st.form("form_udiksar"):
    st.subheader("Data Identitas")
    nama_lengkap = st.text_input("Nama Lengkap")
    
    col1, col2 = st.columns(2)
    with col1:
        tgl_lahir = st.date_input("Tanggal Lahir", min_value=datetime(2000, 1, 1))
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col2:
        wa = st.text_input("No. WhatsApp")
        disabilitas = st.selectbox("Disabilitas", ["Tidak", "Netra", "Rungu", "Daksa", "Grahita", "Lainnya"])
    
    status_nikah = st.selectbox("Status Pernikahan", ["Belum Kawin", "Kawin"])

    st.subheader("Data Pendidikan")
    jenjang_input = st.selectbox("Jenjang Pendidikan", ["SD", "SMP", "SMA/SMK"])
    
    list_angka = ["1", "2", "3", "4", "5", "6"] if jenjang_input == "SD" else ["7", "8", "9"] if jenjang_input == "SMP" else ["10", "11", "12"]
    
    col_edu1, col_edu2 = st.columns(2)
    with col_edu1:
        angka_kelas = st.selectbox("Pilih Kelas", list_angka)
    with col_edu2:
        kelurahan_sekolah = st.selectbox("Kelurahan Sekolah", list(data_sekolah[jenjang_input].keys()))
    
    sekolah_terpilih = st.selectbox("Nama Sekolah", data_sekolah[jenjang_input][kelurahan_sekolah])

    st.subheader("Data Domisili")
    alamat_domisili = st.text_input("Alamat Domisili (RT/RW)")
    detail_alamat = st.text_area("Detail Alamat (Nama Jalan/Blok)")
    
    c1, c2, c3 = st.columns(3)
    with c1: kec = st.text_input("Kecamatan", value="Purwokerto Selatan")
    with c2: kab = st.text_input("Kabupaten", value="Banyumas")
    with c3: prov = st.text_input("Propinsi", value="Jawa Tengah")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- TOMBOL ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        submit = st.form_submit_button("SIMPAN DATA", type="primary", use_container_width=True)

    with col_btn2:
        nomor_wa_pic = "6289665803467" 
        pesan = "Halo PIC CKG, saya butuh bantuan terkait pengisian form pendaftaran."
        link_wa = f"https://wa.me/{nomor_wa_pic}?text={pesan.replace(' ', '%20')}"
        st.markdown(f"""<a href="{link_wa}" target="_blank" class="btn-wa">💬 CONTACT US (WA)</a>""", unsafe_allow_html=True)

    if submit:
        if nama_lengkap and wa and alamat_domisili:
            try:
                # MEMBACA DATA (Otomatis pakai URL di Secrets)
                df_lama = conn.read() 
                
                new_data = {
                    "nama_lengkap": nama_lengkap.upper(),
                    "tanggal_lahir": tgl_lahir.strftime("%Y-%m-%d"),
                    "jenis_kelamin": gender,
                    "no_whatsapp": wa,
                    "status_pernikahan": status_nikah,
                    "disabilitas": disabilitas,
                    "nama_sekolah": sekolah_terpilih,
                    "jenjang_pendidikan": f"KELAS {angka_kelas}", 
                    "alamat_domisili": alamat_domisili,
                    "detail_alamat": detail_alamat,
                    "alamat_sama_sekolah": "Ya",
                    "Propinsi": prov,
                    "kabupaten": kab,
                    "kecamatan": kec,
                    "Kelurahan": kelurahan_sekolah,
                    "ID_TRANSAKSI": str(uuid.uuid4())[:8].upper(),
                    "TIMESTAMP": datetime.now().strftime("%A, %d %B %Y - %H:%M:%S")
                }
                
                updated_df = pd.concat([df_lama, pd.DataFrame([new_data])], ignore_index=True)
                
                # MENGUPDATE DATA (Otomatis pakai kredensial Service Account di Secrets)
                conn.update(data=updated_df)
                
                st.success(f"✅ Data {nama_lengkap} Berhasil Tersimpan!")
                st.balloons()
            except Exception as e:
                st.error(f"Gagal simpan: {e}")
        else:
            st.error("Mohon isi semua data wajib!")
