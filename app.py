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

# --- FUNGSI POP-UP PEMERIKSAAN LENGKAP ---
@st.dialog("📋 FORM PEMERIKSAAN KESEHATAN LENGKAP", width="large")
def form_pemeriksaan_popup():
    st.info("Pastikan Nama & NIK sesuai dengan data registrasi agar sinkron.")
    
    # --- SECTION 1: IDENTITAS DASAR ---
    with st.expander("👤 Identitas Siswa", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            p_nama = st.text_input("Nama Lengkap Siswa").upper()
            p_nik = st.text_input("NIK Siswa (16 Digit)")
        with c2:
            p_sekolah = st.text_input("Nama Sekolah")
            p_kelas = st.selectbox("Kelas", [str(i) for i in range(1, 13)])

    # --- SECTION 2: ANTROPOMETRI & TENSI ---
    with st.expander("⚖️ Gizi & Tekanan Darah", expanded=False):
        c3, c4, c5 = st.columns(3)
        with c3:
            gizi_bb = st.number_input("Berat Badan (kg)", min_value=0.0, step=0.1)
            sistol = st.number_input("Tekanan Darah: Sistol", min_value=0)
        with c4:
            gizi_tb = st.number_input("Tinggi Badan (cm)", min_value=0.0, step=0.1)
            diastol = st.number_input("Tekanan Darah: Diastol", min_value=0)
        with c5:
            kat_imt = st.selectbox("Kategori IMT", ["Sangat Kurus", "Kurus", "Normal", "Gemuk", "Obesitas"])

    # --- SECTION 3: KULIT & TELINGA ---
    with st.expander("👂 Pemeriksaan Fisik (Kulit & Telinga)", expanded=False):
        c6, c7 = st.columns(2)
        with c6:
            rambusia = st.selectbox("Papul Ulkus (Frambusia)", ["Tidak Ada", "Ada"])
            kusta = st.selectbox("Bercak Putih (Kusta)", ["Tidak Ada", "Ada"])
            koreng = st.selectbox("Koreng (Skabies)", ["Tidak Ada", "Ada"])
        with c7:
            telinga_ka = st.selectbox("Telinga Kanan", ["Normal", "Serumen", "Infeksi", "Gangguan Dengar"])
            telinga_ki = st.selectbox("Telinga Kiri", ["Normal", "Serumen", "Infeksi", "Gangguan Dengar"])

    # --- SECTION 4: MATA & GIGI ---
    with st.expander("👁️ Mata & 🦷 Gigi", expanded=False):
        c8, c9 = st.columns(2)
        with c8:
            tajam_ka = st.text_input("Tajam Mata Kanan", value="6/6")
            tajam_ki = st.text_input("Tajam Mata Kiri", value="6/6")
            kaca_mata = st.selectbox("Pakai Kacamata?", ["Tidak", "Ya"])
        with c9:
            gigi_anak = st.selectbox("Kondisi Gigi/Mulut", ["Sehat", "Karies/Berlubang", "Gusi Berdarah", "Lainnya"])
            kebugaran = st.selectbox("Tingkat Kebugaran", ["Baik Sekali", "Baik", "Cukup", "Kurang", "Kurang Sekali"])

    # --- SECTION 5: SKRINING DM (DIABETES) ---
    with st.expander("🩸 Riwayat Kesehatan & GDS", expanded=False):
        c10, c11 = st.columns(2)
        with c10:
            riwayat_dm = st.selectbox("Pernah dinyatakan DM?", ["Tidak", "Ya"])
            kapan_dm = st.text_input("Jika Ya, sudah berapa tahun?", value="-")
        with c11:
            gds_1 = st.number_input("Hasil GDS 1", min_value=0)
            gds_2 = st.number_input("Hasil GDS 2 (Opsional)", min_value=0)
            hasil_hb = st.number_input("Hasil HB", min_value=0.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- LOGIKA PENYIMPANAN PEMERIKSAAN ---
    if st.button("SIMPAN HASIL PEMERIKSAAN", type="primary", use_container_width=True):
        if not p_nama or not p_nik:
            st.error("Nama dan NIK wajib diisi!")
        else:
            # Tentukan Sheet Berdasarkan Kelas (NAMA KAPITAL)
            kls_int = int(p_kelas)
            if kls_int <= 6: target_sheet = "PEMERIKSAAN_SD/MI"
            elif kls_int <= 9: target_sheet = "PEMERIKSAAN_SMP"
            else: target_sheet = "PEMERIKSAAN_SMA/SMK"
            
            master_p_sheet = "MASTER_DATA_PEMERIKSAAN"
            
            # Map data ke kolom Spreadsheet (Urutan sesuai request)
            new_entry = {
                "Nama": p_nama, "NIK": f"'{p_nik}", "Nama Sekolah": p_sekolah, "Kelas": f"KELAS {p_kelas}",
                "Status Daftar": "", "Tiket": "", "Hadir": "", # Kosong sesuai request
                "gizi_bb": gizi_bb, "gizi_tb": gizi_tb, "kategori_imt": kat_imt,
                "sistol": sistol, "diastol": diastol, 
                "ada_papul_ulkus_frambusia": rambusia, "bercak_putih_kusta": kusta, "Koreng_skabies": koreng,
                "gangguan_pendengaran_ka": telinga_ka, "gangguan_pendengaran_ki": telinga_ki,
                "tajam_mata_kanan": tajam_ka, "tajam_mata_kiri": tajam_ki, "kaca_mata": kaca_mata,
                "Pemeriksaan Gigi": gigi_anak, "kebugaran": kebugaran,
                "Pernah_dinyatakan_DM": riwayat_dm, "Jika_ya_berapa_thn": kapan_dm,
                "Hasil_GDS_1": gds_1, "Hasil_GDS_2": gds_2, "hasil_HB": hasil_hb,
                "TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                with st.spinner("Menyimpan hasil pemeriksaan..."):
                    for s in [master_p_sheet, target_sheet]:
                        df_target = conn.read(worksheet=s, ttl=0)
                        df_updated = pd.concat([df_target, pd.DataFrame([new_entry])], ignore_index=True)
                        conn.update(worksheet=s, data=df_updated)
                st.success(f"✅ Data Pemeriksaan {p_nama} Berhasil Disimpan!")
                st.balloons()
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Gagal Simpan! Pastikan Nama Sheet Kapital sudah benar. Error: {e}")

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
                margin-bottom: 35px !important;
            }}

            div[data-testid="stMetric"] {{
                background-color: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid rgba(37, 211, 102, 0.3);
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            [data-testid="stMetricValue"] {{
                color: #25D366 !important;
                font-size: 26px !important;
                width: 100%;
                text-align: center;
            }}
            [data-testid="stMetricLabel"] {{
                color: white !important;
                font-weight: bold !important;
                font-size: 14px !important;
                width: 100%;
                text-align: center;
                white-space: pre-wrap !important;
            }}
            
            h3 {{
                color: #25D366 !important;
                border-bottom: 2px solid #25D366;
                margin-top: 20px;
            }}

            div.stButton > button:first-child {{
                background-color: #FF4B4B;
                color: white;
                border: none;
                height: 45px;
                width: 100%;
                font-weight: bold;
                border-radius: 10px;
            }}

            /* Tombol Khusus Input Pemeriksaan (Cyan/Biru) */
            .stButton > button[kind="secondary"] {{
                background-color: #00ADB5 !important;
                color: white !important;
                border: none !important;
            }}
            
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

# --- HEADER ---
st.markdown("<h1>🏥 CKG SEKOLAH PUSKESMAS PWT SELATAN</h1>", unsafe_allow_html=True)

# --- RINGKASAN DATA (ATAS) ---
try:
    df_global = conn.read(worksheet="MASTER_DATA", ttl=0)
    c_sd = len(df_global[df_global['jenjang_pendidikan'].str.contains('KELAS 1|KELAS 2|KELAS 3|KELAS 4|KELAS 5|KELAS 6', na=False)])
    c_smp = len(df_global[df_global['jenjang_pendidikan'].str.contains('KELAS 7|KELAS 8|KELAS 9', na=False)])
    c_sma = len(df_global[df_global['jenjang_pendidikan'].str.contains('KELAS 10|KELAS 11|KELAS 12', na=False)])

    m1, m2, m3 = st.columns(3)
    with m1: st.metric(label="Total SD/MI\n(Terinput)", value=f"{c_sd}")
    with m2: st.metric(label="Total SMP\n(Terinput)", value=f"{c_smp}")
    with m3: st.metric(label="Total SMA/SMK\n(Terinput)", value=f"{c_sma}")
    st.markdown("<br>", unsafe_allow_html=True)
except:
    st.info("📊 Menghubungkan ke database...")

# --- DATABASE SEKOLAH (OMITTED FOR BREVITY - SAMA SEPERTI KODE ABANG) ---
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

# --- TOMBOL MENU UTAMA ---
col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    submit = st.button("SIMPAN DATA", type="primary", use_container_width=True)
with col_btn2:
    if st.button("📝 INPUT PEMERIKSAAN", use_container_width=True):
        form_pemeriksaan_popup()
with col_btn3:
    st.markdown(f"""<a href="https://wa.me/6289665803467" target="_blank" class="btn-wa">💬 CONTACT WA</a>""", unsafe_allow_html=True)

# --- LOGIKA PENYIMPANAN REGISTRASI ---
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

# --- BAGIAN FILTER CEK SISWA (BAWAH) ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.subheader("🔍 CEK DATA SISWA TERDAFTAR")
try:
    df_look = conn.read(worksheet="MASTER_DATA", ttl=0)
    c1, c2, c3 = st.columns(3)
    with c1: v_jen = st.selectbox("Pilih Jenjang", ["-- Pilih --", "SD/MI", "SMP", "SMA/SMK"], key="v_jen")
    with c2:
        if v_jen != "-- Pilih --":
            sekolah_list = []
            for kel in data_sekolah[v_jen]: sekolah_list.extend(data_sekolah[v_jen][kel])
            v_sch = st.selectbox("Pilih Sekolah", ["-- Pilih --"] + sorted(list(set(sekolah_list))), key="v_sch")
        else:
            st.selectbox("Pilih Sekolah", ["-- Pilih Jenjang Dulu --"], disabled=True)
            v_sch = "-- Pilih --"
    with c3:
        if v_jen != "-- Pilih --":
            kls_list = ["1", "2", "3", "4", "5", "6"] if v_jen == "SD/MI" else (["7", "8", "9"] if v_jen == "SMP" else ["10", "11", "12"])
            v_kls = st.selectbox("Pilih Kelas", ["-- Pilih --"] + kls_list, key="v_kls")
        else:
            st.selectbox("Pilih Kelas", ["-- Pilih Jenjang Dulu --"], disabled=True)
            v_kls = "-- Pilih --"

    if v_jen != "-- Pilih --" and v_sch != "-- Pilih --" and v_kls != "-- Pilih --":
        mask = (df_look['nama_sekolah'] == v_sch) & (df_look['jenjang_pendidikan'] == f"KELAS {v_kls}")
        hasil = df_look[mask][['nama_lengkap', 'jenjang_pendidikan']].reset_index(drop=True)
        hasil.columns = ['NAMA SISWA', 'KELAS']
        if not hasil.empty:
            st.success(f"Ditemukan {len(hasil)} siswa terdaftar.")
            st.dataframe(hasil, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada data siswa untuk filter ini.")
except:
    st.write("Belum ada data pendaftar.")
