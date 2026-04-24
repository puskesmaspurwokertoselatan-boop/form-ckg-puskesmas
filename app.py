import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import base64
import time 

# --- CONFIG ---
st.set_page_config(page_title="Form UDIKSAR CKG PUSKESMAS", layout="centered")

# --- INITIALIZE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI CACHE DATA ---
@st.cache_data(ttl=300)
def get_cached_data(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()

# --- INITIALIZE SESSION STATE ---
if 'form_idx' not in st.session_state:
    st.session_state.form_idx = 0
if 'show_pemeriksaan_form' not in st.session_state:
    st.session_state.show_pemeriksaan_form = False
# Inisialisasi sisa_ed agar tidak error saat aplikasi pertama kali dimuat
if 'sisa_ed' not in st.session_state:
    st.session_state.sisa_ed = 2

def reset_form():
    st.session_state.form_idx += 1
    st.cache_data.clear()

# --- FUNGSI POP-UP DIALOGS ---
@st.dialog("⚠️ DATA SUDAH TERDAFTAR")
def show_duplicate_popup(nama, nik):
    st.warning(f"NIK **{nik}** atas nama **{nama}** sudah terdata di sistem kami.")
    if st.button("KOSONGKAN FORMULIR", use_container_width=True):
        reset_form()
        st.rerun()

@st.dialog("✅ PENDAFTARAN BERHASIL!")
def show_success_pendaftaran(nama):
    st.success(f"Selamat! Data **{nama}** telah berhasil dikirim.")
    st.info("Pastikan data yang diinput sudah benar untuk keperluan skrining Kemenkes.")
    if st.button("KEMBALI KE BERANDA", use_container_width=True):
        reset_form()
        st.rerun()

@st.dialog("📋 FORM PEMERIKSAAN KESEHATAN", width="large")
def form_pemeriksaan_popup():
    st.warning("⚠️ **Input Pemeriksaan ini khusus diisi oleh petugas kesehatan Puskesmas Purwokerto Selatan.**")
    st.info("Gunakan NIK atau Nama untuk mencari data siswa.")
    try:
        df_ref = get_cached_data("MASTER_DATA")
        df_ref['nik_clean'] = df_ref['nik'].astype(str).str.replace("'", "")
    except:
        st.error("Gagal terhubung ke database.")
        return

    v_nik, v_nama, v_sekolah, v_kelas, v_tiket = "", "", "", "1", ""
    m_cari = st.radio("Metode Pencarian:", ["NIK", "Nama Lengkap"], horizontal=True, key="radio_cari_pemeriksaan")

    if m_cari == "NIK":
        s_nik = st.text_input("Input NIK 16 Digit", key="input_nik_pemeriksaan").strip()
        if len(s_nik) == 16:
            m = df_ref[df_ref['nik_clean'] == s_nik]
            if not m.empty:
                r = m.iloc[0]
                v_nik, v_nama, v_sekolah = s_nik, r['nama_lengkap'], r['nama_sekolah']
                v_kelas = str(r['jenjang_pendidikan']).replace("KELAS ", "")
                v_tiket = str(r.get('ID_TRANSAKSI', ''))
                st.success(f"Siswa Ditemukan: {v_nama}")
    else:
        s_nama = st.text_input("Ketik Nama Siswa...", key="input_nama_pemeriksaan").upper()
        if s_nama:
            hits = df_ref[df_ref['nama_lengkap'].str.contains(s_nama, na=False)]
            if not hits.empty:
                sel_nama = st.selectbox("Pilih Nama Sesuai:", ["-- Pilih --"] + hits['nama_lengkap'].tolist(), key="select_nama_pemeriksaan")
                if sel_nama != "-- Pilih --":
                    r = hits[hits['nama_lengkap'] == sel_nama].iloc[0]
                    v_nik, v_nama, v_sekolah = r['nik_clean'], r['nama_lengkap'], r['nama_sekolah']
                    v_kelas = str(r['jenjang_pendidikan']).replace("KELAS ", "")
                    v_tiket = str(r.get('ID_TRANSAKSI', ''))

    st.markdown("---")
    
    if v_nik:
        with st.form("form_aksi_pemeriksaan"):
            st.markdown("### 👤 Data Siswa", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.text_input("NIK", value=v_nik, disabled=True)
            c2.text_input("Nama Lengkap", value=v_nama, disabled=True)
            c1.text_input("Sekolah", value=v_sekolah, disabled=True)
            c2.text_input("Kelas", value=f"KELAS {v_kelas}", disabled=True)
            c1.text_input("No Tiket", value=v_tiket, disabled=True)
            
            st.markdown("### 🩺 Hasil Pemeriksaan", unsafe_allow_html=True)
            gizi_c1, gizi_c2 = st.columns(2)
            gizi_bb = gizi_c1.number_input("Berat Badan (gizi_bb) Kg", min_value=0.0, format="%.1f")
            gizi_tb = gizi_c2.number_input("Tinggi Badan (gizi_tb) cm", min_value=0.0, format="%.1f")
            
            ukur_c1, ukur_c2 = st.columns(2)
            lk = ukur_c1.number_input("Lingkar Kepala (lk) cm", min_value=0.0, format="%.1f")
            lp = ukur_c2.number_input("Lingkar Perut (lp) cm", min_value=0.0, format="%.1f")
            
            tensi_c1, tensi_c2 = st.columns(2)
            sistol = tensi_c1.number_input("Sistol", min_value=0)
            diastol = tensi_c2.number_input("Diastol", min_value=0)
            
            kusta_c1, kusta_c2 = st.columns(2)
            frambusia = kusta_c1.selectbox("Ada Papul Ulkus Frambusia?", ["Tidak Ada", "Ada"])
            kusta = kusta_c2.selectbox("Bercak Putih Kusta?", ["Tidak Ada", "Ada"])
            skabies = kusta_c1.selectbox("Koreng Skabies?", ["Tidak Ada", "Ada"])
            
            dengar_c1, dengar_c2 = st.columns(2)
            dengar_ka = dengar_c1.selectbox("Gangguan Pendengaran Kanan?", ["Normal", "Tidak Normal"])
            dengar_ki = dengar_c2.selectbox("Gangguan Pendengaran Kiri?", ["Normal", "Tidak Normal"])
            
            mata_c1, mata_c2 = st.columns(2)
            mata_ka = mata_c1.selectbox("Tajam Mata Kanan?", ["Normal", "Tidak Normal"])
            mata_ki = mata_c2.selectbox("Tajam Mata Kiri?", ["Normal", "Tidak Normal"])
            kaca_mata = mata_c1.selectbox("Pakai Kacamata?", ["Tidak", "Iya"])
            
            gigi = st.selectbox("Pemeriksaan Gigi", ["Bagus", "Caries", "Gigi Berlubang", "Gigi Goyang", "Gigi Tumpang"])
            
            dm_c1, dm_c2 = st.columns(2)
            dm = dm_c1.selectbox("Pernah Dinyatakan DM?", ["Tidak", "Iya"])
            lama_dm = dm_c2.number_input("Berapa Tahun DM? (Kosongkan jika Tidak)", min_value=0) if dm == "Iya" else 0
            
            hasil_c1, hasil_c2 = st.columns(2)
            gds = hasil_c1.number_input("Hasil GDS 1", min_value=0.0, format="%.1f")
            hb = hasil_c2.number_input("Hasil HB", min_value=0.0, format="%.1f")
            hasil = st.text_input("Hasil / Catatan Lainnya")
            
            if st.form_submit_button("SIMPAN HASIL PEMERIKSAAN", type="primary", use_container_width=True):
                with st.spinner("Menyimpan ke database pemeriksaan..."):
                    try:
                        df_pem = conn.read(worksheet="MASTER_DATA_PEMERIKSAAN", ttl=0)
                        
                        # Data yang akan diinput
                        new_data = {
                            "Nama": v_nama,
                            "NIK": f"'{v_nik}",
                            "Nama Sekolah": v_sekolah,
                            "Kelas": f"KELAS {v_kelas}",
                            "Status Daftar": "Selesai",
                            "Tiket": v_tiket,
                            "Hadir": "Hadir",
                            "gizi_bb": gizi_bb,
                            "gizi_tb": gizi_tb,
                            "lk": lk,
                            "lp": lp,
                            "sistol": sistol,
                            "diastol": diastol,
                            "ada_papul_ulkus_frambusia": frambusia,
                            "bercak_putih_kusta": kusta,
                            "Koreng_skabies": skabies,
                            "gangguan_pendengaran_ka": dengar_ka,
                            "gangguan_pendengaran_ki": dengar_ki,
                            "tajam_mata_kanan": mata_ka,
                            "tajam_mata_kiri": mata_ki,
                            "kaca_mata": kaca_mata,
                            "Pemeriksaan Gigi": gigi,
                            "Pernah_dinyatakan_DM": dm,
                            "Lama_DM": lama_dm,
                            "Hasil_GDS_1": gds,
                            "Hasil": hasil,
                            "hasil_HB": hb
                        }
                        
                        # SMART MAPPING: Cocokkan nama kolom (case-insensitive) agar tidak ada duplikasi kolom
                        actual_cols = {str(c).lower().strip(): c for c in df_pem.columns}
                        
                        mapped_data = {}
                        for k, v in new_data.items():
                            lower_k = k.lower().strip()
                            if lower_k in actual_cols:
                                mapped_data[actual_cols[lower_k]] = v
                            else:
                                mapped_data[k] = v # Jika kolom benar-benar belum ada, buat baru pakai teks asli
                                
                        upd_pem = pd.concat([df_pem, pd.DataFrame([mapped_data])], ignore_index=True)
                        conn.update(worksheet="MASTER_DATA_PEMERIKSAAN", data=upd_pem)
                        
                        st.success(f"Data Pemeriksaan {v_nama} Berhasil Disimpan!")
                        time.sleep(2)
                        st.session_state.show_pemeriksaan_form = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Koneksi Database bermasalah: {str(e)}")

# --- STYLING ---
def apply_ui_style(main_bg_img):
    bg_css = ""
    try:
        with open(main_bg_img, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        bg_css = f"""
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        """
    except: 
        pass

    st.markdown(f"""
        <style>
        [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
        footer {{visibility: hidden;}}
        {bg_css}
        .stMainBlockContainer {{
            background-color: rgba(15, 15, 15, 0.9);
            padding: 2rem !important;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        .form-card {{
            background-color: rgba(255, 255, 255, 0.08);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            border-left: 6px solid #25D366;
        }}
        .form-card h3 {{
            margin-top: 0px !important;
            color: #25D366 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
        }}
        h1 {{ color: #FFFFFF !important; text-align: center; margin-bottom: 30px !important; }}
        
        .stButton > button[kind="secondary"] {{
            background-color: #FF8C00 !important;
            color: white !important;
            border: none !important;
        }}
        
        .btn-wa {{
            background-color: #25D366; color: white !important; border-radius: 10px;
            text-decoration: none; display: flex; align-items: center; justify-content: center;
            font-weight: bold; height: 45px; width: 100%;
        }}
        </style>
        """, unsafe_allow_html=True)

apply_ui_style("IMG_20260402_084603.jpg")

# --- APP START ---
if st.session_state.show_pemeriksaan_form:
    st.session_state.show_pemeriksaan_form = False
    form_pemeriksaan_popup()

st.markdown("<h1>🏥 FORM DIGITAL UDIKSAR CKG</h1>", unsafe_allow_html=True)

# Dashboard Metrics
try:
    df_db = get_cached_data("MASTER_DATA")
    if not df_db.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Siswa SD/MI", len(df_db[df_db['jenjang_pendidikan'].isin([f"KELAS {i}" for i in range(1, 7)])]))
        c2.metric("Siswa SMP", len(df_db[df_db['jenjang_pendidikan'].isin([f"KELAS {i}" for i in range(7, 10)])]))
        c3.metric("Siswa SMA/SMK", len(df_db[df_db['jenjang_pendidikan'].isin([f"KELAS {i}" for i in range(10, 13)])]))
except: pass

# --- DATABASE SEKOLAH ---
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

# --- SECTION 1: DATA DIRI ---
fk = st.session_state.form_idx
st.markdown('<div class="form-card"><h3>📋 Informasi Data Diri</h3>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
nm = c1.text_input("Nama Lengkap Siswa", placeholder="Sesuai Akta Lahir", key=f"nm_{fk}")
ni = c2.text_input("Nomor Induk Kependudukan (NIK)", placeholder="16 Digit", key=f"ni_{fk}")

# UPDATE 1: Tahun lahir dimulai dari 1999
try:
    tg = c1.date_input("Tanggal Lahir", value=None, min_value=datetime(1999, 1, 1), key=f"tg_{fk}")
except:
    tg = c1.date_input("Tanggal Lahir", min_value=datetime(1999, 1, 1), key=f"tg_fallback_{fk}")

gn = c1.selectbox("Jenis Kelamin", ["-- Pilih --", "Laki-laki", "Perempuan"], key=f"gn_{fk}")
wa = c2.text_input("WhatsApp Aktif", placeholder="08...", key=f"wa_{fk}")
ds = c2.selectbox("Status Disabilitas", ["Tidak", "Netra", "Rungu", "Daksa", "Grahita", "Lainnya"], key=f"ds_{fk}")
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 2: DATA SEKOLAH ---
st.markdown('<div class="form-card"><h3>🏫 Informasi Pendidikan</h3>', unsafe_allow_html=True)
jn = st.selectbox("Pilih Jenjang Sekolah", ["-- Pilih Jenjang --", "SD/MI", "SMP", "SMA/SMK"], index=0, key=f"jn_{fk}")
ks, kl, sk = "-- Pilih --", "-- Pilih --", "-- Pilih --"

if jn != "-- Pilih Jenjang --":
    col_a, col_b = st.columns(2)
    l_kls = ["1", "2", "3", "4", "5", "6"] if jn == "SD/MI" else (["7", "8", "9"] if jn == "SMP" else ["10", "11", "12"])
    ks = col_a.selectbox("Kelas Saat Ini", ["-- Pilih Kelas --"] + l_kls, key=f"ks_{fk}")
    kl = col_b.selectbox("Kelurahan Sekolah", ["-- Pilih Kelurahan --"] + list(data_sekolah[jn].keys()), key=f"kl_{fk}")
    
    if kl != "-- Pilih Kelurahan --":
        sk = st.selectbox("Nama Instansi Sekolah", ["-- Pilih Sekolah --"] + data_sekolah[jn][kl], key=f"sk_{fk}")
else:
    st.info("Silakan pilih Jenjang Sekolah terlebih dahulu.")
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 3: DOMISILI ---
st.markdown('<div class="form-card"><h3>🏠 Informasi Tempat Tinggal</h3>', unsafe_allow_html=True)
dom_c1, dom_c2 = st.columns(2)
propinsi = dom_c1.text_input("Provinsi", placeholder="Contoh: Jawa Tengah", key=f"prop_{fk}")
kabupaten = dom_c2.text_input("Kabupaten/Kota", placeholder="Contoh: Banyumas", key=f"kab_{fk}")
kecamatan = dom_c1.text_input("Kecamatan", key=f"kec_{fk}")
kelurahan = dom_c2.text_input("Kelurahan/Desa", key=f"kel_{fk}")
dm = st.text_input("Alamat Singkat (RT/RW)", key=f"dm_{fk}")
dt = st.text_area("Detail Alamat Lengkap", key=f"dt_{fk}")
st.markdown('</div>', unsafe_allow_html=True)

# --- TOMBOL AKSI ---
st.markdown("<br>", unsafe_allow_html=True)
btn_c1, btn_c2 = st.columns(2)

if btn_c1.button("💾 SIMPAN DATA PENDAFTARAN", type="primary", use_container_width=True):
    inv = ["-- Pilih --", "-- Pilih Jenjang --", "-- Pilih Kelas --", "-- Pilih Kelurahan --", "-- Pilih Sekolah --", "", None]
    if any(x in inv for x in [nm, jn, ks, sk]) or len(ni) != 16:
        st.error("Gagal! Mohon lengkapi seluruh data wajib dan pastikan NIK 16 digit.")
    else:
        try:
            with st.spinner("Sedang memproses..."):
                df_check = conn.read(worksheet="MASTER_DATA", ttl=0)
                if ni in df_check['nik'].astype(str).str.replace("'", "").tolist():
                    show_duplicate_popup(nm, ni)
                else:
                    new_row = {
                        "nik": f"'{ni}", "nama_lengkap": nm.upper(), "tanggal_lahir": str(tg),
                        "jenis_kelamin": str(gn), "no_whatsapp": f"'{wa}", "disabilitas": str(ds),
                        "nama_sekolah": sk, "jenjang_pendidikan": f"KELAS {ks}",
                        "propinsi": propinsi, "kabupaten": kabupaten, "kecamatan": kecamatan, "kelurahan": kelurahan,
                        "alamat_domisili": dm, "detail_alamat": dt, "kesempatan_update": 2,
                        "TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ID_TRANSAKSI": str(uuid.uuid4())[:8].upper()
                    }
                    upd = pd.concat([df_check, pd.DataFrame([new_row])], ignore_index=True)
                    conn.update(worksheet="MASTER_DATA", data=upd)
                    show_success_pendaftaran(nm)
        except: st.error("Koneksi Database bermasalah.")

btn_c2.markdown('<a href="https://wa.me/6289665803467" class="btn-wa">💬 HUBUNGI ADMIN WHATSAPP</a>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
btn_c3, btn_c4 = st.columns(2)

if btn_c3.button("📋 INPUT PEMERIKSAAN KESEHATAN", use_container_width=True, key="btn_pemeriksaan_main"):
    st.session_state.show_pemeriksaan_form = True
    st.rerun()

# --- MENU EDIT DATA SISWA ---
with btn_c4.expander("✏️ MENU EDIT DATA SISWA"):
    ed_nik = st.text_input("Input NIK untuk Koreksi", key="search_edit_nik")
    if st.button("CARI & EDIT DATA", type="secondary", use_container_width=True, key="btn_cari_edit"):
        if len(ed_nik) == 16:
            df_ed = conn.read(worksheet="MASTER_DATA", ttl=0)
            df_ed['nik_c'] = df_ed['nik'].astype(str).str.replace("'", "")
            idx = df_ed.index[df_ed['nik_c'] == ed_nik].tolist()
            if idx:
                st.session_state.idx_ed = idx[0]
                
                # Logika aman untuk kesempatan_update
                raw_val = df_ed.iloc[idx[0]].get('kesempatan_update')
                if pd.isna(raw_val):
                    st.session_state.sisa_ed = 2
                else:
                    st.session_state.sisa_ed = int(raw_val)
                    
                if st.session_state.sisa_ed <= 0: st.error("Kesempatan edit habis.")
                else: st.success("Data ditemukan! Form muncul di bawah.")
            else: st.error("NIK tidak terdaftar.")

if 'idx_ed' in st.session_state:
    st.markdown('<div class="form-card"><h3>🖊️ Perbaikan Seluruh Data</h3>', unsafe_allow_html=True)
    with st.form("full_edit_form"):
        df_m = conn.read(worksheet="MASTER_DATA", ttl=0)
        curr = df_m.iloc[st.session_state.idx_ed]
        
        def safe_str(val):
            return "" if pd.isna(val) else str(val)
            
        clean_nik = safe_str(curr.get('nik')).replace("'", "")
        clean_wa = safe_str(curr.get('no_whatsapp')).replace("'", "")
        
        col_ed1, col_ed2 = st.columns(2)
        u_nm = col_ed1.text_input("Nama Lengkap", value=safe_str(curr.get('nama_lengkap')))
        u_ni = col_ed2.text_input("NIK (16 Digit)", value=clean_nik)
        
        try:
            val_tgl = pd.to_datetime(curr['tanggal_lahir']).date()
        except:
            val_tgl = datetime(1999, 1, 1).date()
        # Tahun lahir minimal 1999 juga berlaku di menu edit
        try:
            u_tg = col_ed1.date_input("Tanggal Lahir", value=val_tgl, min_value=datetime(1999, 1, 1))
        except:
            u_tg = col_ed1.date_input("Tanggal Lahir", min_value=datetime(1999, 1, 1))
        
        u_wa = col_ed2.text_input("WhatsApp", value=clean_wa)
        u_sk = col_ed1.text_input("Nama Sekolah", value=safe_str(curr.get('nama_sekolah')))
        u_ks = col_ed2.text_input("Kelas (Contoh: KELAS 1)", value=safe_str(curr.get('jenjang_pendidikan')))
        
        col_ed3, col_ed4 = st.columns(2)
        u_prop = col_ed3.text_input("Provinsi", value=safe_str(curr.get('propinsi')))
        u_kab = col_ed4.text_input("Kabupaten/Kota", value=safe_str(curr.get('kabupaten')))
        u_kec = col_ed3.text_input("Kecamatan", value=safe_str(curr.get('kecamatan')))
        u_kel = col_ed4.text_input("Kelurahan/Desa", value=safe_str(curr.get('kelurahan')))
        
        u_dm = st.text_input("Alamat (RT/RW)", value=safe_str(curr.get('alamat_domisili')))
        u_dt = st.text_area("Detail Alamat", value=safe_str(curr.get('detail_alamat')))
        
        st.warning(f"⚠️ Sisa kesempatan edit Anda: {st.session_state.sisa_ed} kali.")
        
        if st.form_submit_button("SIMPAN PERUBAHAN DATA", use_container_width=True):
            if len(u_ni.strip()) != 16:
                st.error("NIK harus 16 digit!")
            else:
                # Pastikan tipe data kolom adalah object untuk menghindari Pandas dtype incompatibility error
                for col in ['nama_lengkap', 'nik', 'tanggal_lahir', 'no_whatsapp', 'nama_sekolah', 'jenjang_pendidikan', 'propinsi', 'kabupaten', 'kecamatan', 'kelurahan', 'alamat_domisili', 'detail_alamat', 'kesempatan_update']:
                    if col not in df_m.columns:
                        df_m[col] = ""
                    df_m[col] = df_m[col].astype('object')
                    
                df_m.at[st.session_state.idx_ed, 'nama_lengkap'] = u_nm.upper()
                df_m.at[st.session_state.idx_ed, 'nik'] = f"'{u_ni.strip()}"
                df_m.at[st.session_state.idx_ed, 'tanggal_lahir'] = str(u_tg)
                df_m.at[st.session_state.idx_ed, 'no_whatsapp'] = f"'{u_wa.strip()}"
                df_m.at[st.session_state.idx_ed, 'nama_sekolah'] = u_sk
                df_m.at[st.session_state.idx_ed, 'jenjang_pendidikan'] = u_ks
                df_m.at[st.session_state.idx_ed, 'propinsi'] = u_prop
                df_m.at[st.session_state.idx_ed, 'kabupaten'] = u_kab
                df_m.at[st.session_state.idx_ed, 'kecamatan'] = u_kec
                df_m.at[st.session_state.idx_ed, 'kelurahan'] = u_kel
                df_m.at[st.session_state.idx_ed, 'alamat_domisili'] = u_dm
                df_m.at[st.session_state.idx_ed, 'detail_alamat'] = u_dt
                df_m.at[st.session_state.idx_ed, 'kesempatan_update'] = st.session_state.sisa_ed - 1
                
                conn.update(worksheet="MASTER_DATA", data=df_m)
                st.success("Update Berhasil!")
                del st.session_state.idx_ed
                time.sleep(1)
                reset_form()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- FILTER DATA ---
# UPDATE 2: Penambahan kolom filter Kelas
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("🔍 CEK DAFTAR SISWA TERDAFTAR"):
    df_l = get_cached_data("MASTER_DATA")
    if not df_l.empty:
        f1, f2, f3 = st.columns(3)
        j_f = f1.selectbox("Filter Jenjang", ["-- Pilih Jenjang --", "SD/MI", "SMP", "SMA/SMK"], key="jf_filter")
        
        if j_f != "-- Pilih Jenjang --":
            # Filter sekolah berdasarkan jenjang pendidikan
            if j_f == "SD/MI": kls_target = [f"KELAS {i}" for i in range(1, 7)]
            elif j_f == "SMP": kls_target = [f"KELAS {i}" for i in range(7, 10)]
            else: kls_target = [f"KELAS {i}" for i in range(10, 13)]
            
            df_filtered_jenjang = df_l[df_l['jenjang_pendidikan'].isin(kls_target)]
            sch_list = sorted(df_filtered_jenjang['nama_sekolah'].unique())
            
            s_f = f2.selectbox("Pilih Nama Sekolah", ["-- Pilih Sekolah --"] + sch_list, key="sf_filter")
            
            if s_f != "-- Pilih Sekolah --":
                # Cari kelas yang tersedia di sekolah tersebut
                df_filtered_sch = df_filtered_jenjang[df_filtered_jenjang['nama_sekolah'] == s_f]
                kls_list = sorted(df_filtered_sch['jenjang_pendidikan'].unique())
                
                c_f = f3.selectbox("Pilih Kelas", ["Semua Kelas"] + kls_list, key="cf_filter")
                
                # Eksekusi filter akhir
                res = df_filtered_sch.copy()
                if c_f != "Semua Kelas":
                    res = res[res['jenjang_pendidikan'] == c_f]
                
                st.dataframe(res[['nama_lengkap', 'jenjang_pendidikan']], use_container_width=True, hide_index=True)
            else:
                st.info("Pilih Nama Sekolah untuk melihat daftar.")
        else:
            st.info("Pilih Jenjang terlebih dahulu.")
