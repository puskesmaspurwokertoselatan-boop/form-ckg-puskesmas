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
    st.info("Gunakan NIK atau Nama untuk mencari data siswa.")
    try:
        df_ref = get_cached_data("MASTER_DATA")
        df_ref['nik_clean'] = df_ref['nik'].astype(str).str.replace("'", "")
    except:
        st.error("Gagal terhubung ke database.")
        return

    v_nik, v_nama, v_sekolah, v_kelas = "", "", "", "1"
    m_cari = st.radio("Metode Pencarian:", ["NIK", "Nama Lengkap"], horizontal=True, key="radio_cari_pemeriksaan")

    if m_cari == "NIK":
        s_nik = st.text_input("Input NIK 16 Digit", key="input_nik_pemeriksaan").strip()
        if len(s_nik) == 16:
            m = df_ref[df_ref['nik_clean'] == s_nik]
            if not m.empty:
                v_nik, v_nama, v_sekolah = s_nik, m['nama_lengkap'].values[0], m['nama_sekolah'].values[0]
                v_kelas = str(m['jenjang_pendidikan'].values[0]).replace("KELAS ", "")
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

    st.markdown("---")
    c1, c2 = st.columns(2)
    p_nik = c1.text_input("NIK Konfirmasi", value=v_nik, key="nik_konf_pemeriksaan")
    p_nama = c2.text_input("Nama Konfirmasi", value=v_nama, key="nama_konf_pemeriksaan").upper()
    
    if st.button("SIMPAN HASIL PEMERIKSAAN", type="primary", use_container_width=True, key="btn_save_pemeriksaan"):
        st.info("Fungsi simpan pemeriksaan sedang diproses...")

# --- STYLING ---
def apply_ui_style(main_bg_img):
    try:
        with open(main_bg_img, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        st.markdown(f"""
            <style>
            [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
            footer {{visibility: hidden;}}
            .stApp {{
                background: url("data:image/png;base64,{bin_str}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
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
    except: pass

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
        c1.metric("Siswa SD/MI", len(df_db[df_db['jenjang_pendidikan'].str.contains('1|2|3|4|5|6', na=False)]))
        c2.metric("Siswa SMP", len(df_db[df_db['jenjang_pendidikan'].str.contains('7|8|9', na=False)]))
        c3.metric("Siswa SMA/SMK", len(df_db[df_db['jenjang_pendidikan'].str.contains('10|11|12', na=False)]))
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

# Proteksi Tanggal
try:
    tg = c1.date_input("Tanggal Lahir", value=None, key=f"tg_{fk}")
except:
    tg = c1.date_input("Tanggal Lahir", key=f"tg_fallback_{fk}")

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

# --- MENU EDIT DATA SISWA (ANTI-ERROR EDITION) ---
with btn_c4.expander("✏️ MENU EDIT DATA SISWA"):
    ed_nik = st.text_input("Input NIK untuk Koreksi", key="search_edit_nik")
    if st.button("CARI & EDIT DATA", type="secondary", use_container_width=True, key="btn_cari_edit"):
        if len(ed_nik) == 16:
            df_ed = conn.read(worksheet="MASTER_DATA", ttl=0)
            df_ed['nik_c'] = df_ed['nik'].astype(str).str.replace("'", "")
            idx = df_ed.index[df_ed['nik_c'] == ed_nik].tolist()
            if idx:
                st.session_state.idx_ed = idx[0]
                st.session_state.sisa_ed = int(df_ed.iloc[idx[0]].get('kesempatan_update', 2))
                if st.session_state.sisa_ed <= 0: st.error("Kesempatan edit habis.")
                else: st.success("Data ditemukan! Form muncul di bawah.")
            else: st.error("NIK tidak terdaftar.")

if 'idx_ed' in st.session_state:
    st.markdown('<div class="form-card"><h3>🖊️ Perbaikan Seluruh Data</h3>', unsafe_allow_html=True)
    with st.form("full_edit_form"):
        # Ambil data FRESH dari server untuk edit
        df_m = conn.read(worksheet="MASTER_DATA", ttl=0)
        curr = df_m.iloc[st.session_state.idx_ed]
        
        # Bersihkan data dari tanda petik agar tidak double saat simpan ulang
        clean_nik = str(curr['nik']).replace("'", "")
        clean_wa = str(curr['no_whatsapp']).replace("'", "")
        
        col_ed1, col_ed2 = st.columns(2)
        u_nm = col_ed1.text_input("Nama Lengkap", value=curr['nama_lengkap'])
        u_ni = col_ed2.text_input("NIK (16 Digit)", value=clean_nik)
        
        # Handle Tanggal Lahir (Cegah Crash jika format salah)
        try:
            val_tgl = pd.to_datetime(curr['tanggal_lahir']).date()
        except:
            val_tgl = None
        u_tg = col_ed1.date_input("Tanggal Lahir", value=val_tgl)
        
        u_wa = col_ed2.text_input("WhatsApp", value=clean_wa)
        u_sk = col_ed1.text_input("Nama Sekolah", value=curr['nama_sekolah'])
        u_ks = col_ed2.text_input("Kelas (Contoh: KELAS 1)", value=curr['jenjang_pendidikan'])
        u_dm = st.text_input("Alamat (RT/RW)", value=curr['alamat_domisili'])
        u_dt = st.text_area("Detail Alamat", value=curr['detail_alamat'])
        
        st.warning(f"⚠️ Sisa kesempatan edit Anda: {st.session_state.sisa_ed} kali.")
        
        if st.form_submit_button("SIMPAN PERUBAHAN DATA", use_container_width=True):
            if len(u_ni.strip()) != 16:
                st.error("NIK harus 16 digit!")
            else:
                df_m.at[st.session_state.idx_ed, 'nama_lengkap'] = u_nm.upper()
                df_m.at[st.session_state.idx_ed, 'nik'] = f"'{u_ni.strip()}"
                df_m.at[st.session_state.idx_ed, 'tanggal_lahir'] = str(u_tg)
                df_m.at[st.session_state.idx_ed, 'no_whatsapp'] = f"'{u_wa.strip()}"
                df_m.at[st.session_state.idx_ed, 'nama_sekolah'] = u_sk
                df_m.at[st.session_state.idx_ed, 'jenjang_pendidikan'] = u_ks
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
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("🔍 CEK DAFTAR SISWA TERDAFTAR"):
    df_l = get_cached_data("MASTER_DATA")
    if not df_l.empty:
        f1, f2 = st.columns(2)
        j_f = f1.selectbox("Filter Jenjang", ["-- Pilih Jenjang --", "SD/MI", "SMP", "SMA/SMK"], key="jf_filter")
        if j_f != "-- Pilih Jenjang --":
            sch_list = sorted(df_l[df_l['nama_sekolah'].notna()]['nama_sekolah'].unique())
            s_f = f2.selectbox("Pilih Nama Sekolah", ["-- Pilih Sekolah --"] + sch_list, key="sf_filter")
            if s_f != "-- Pilih Sekolah --":
                res = df_l[df_l['nama_sekolah'] == s_f]
                st.dataframe(res[['nama_lengkap', 'jenjang_pendidikan']], use_container_width=True, hide_index=True)
            else:
                st.info("Pilih Nama Sekolah untuk melihat daftar.")
        else:
            st.info("Pilih Jenjang terlebih dahulu.")
