import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Dashboard Analisis Data TBC")
st.markdown("""
Aplikasi ini memungkinkan Anda mengunggah file CSV/Excel, melakukan pembersihan data, melakukan penilaian 
untuk kategori Rumah, Sanitasi, dan Perilaku, serta menampilkan visualisasi hasil analisis.
""")

# ----- 1. Unggah File -----
uploaded_file = st.file_uploader("Pilih file CSV/Excel", type=["csv", "xlsx"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=";")
        else:
            df = pd.read_excel(uploaded_file)
        st.success("File berhasil diunggah!")
        st.write("Data asli (5 baris pertama):", df.head())
    except Exception as e:
        st.error(f"Error membaca file: {e}")
    
    # ----- 2. Cleaning Data -----
    st.markdown("### Proses Cleaning Data")
    df_clean = df.copy()
    df_clean = df_clean.dropna()
    df_clean.columns = df_clean.columns.str.strip()
    st.write("Data setelah cleaning (5 baris pertama):", df_clean.head())
    
    # ----- 3. Fungsi Penilaian -----
    def nilai_rumah(val):
        sangat_buruk = ['Tidak ada', 'Tanah', 'Kurang Baik', 'Bukan tembok', 'Tidak Ada',
                        'Kurang terang', 'Semi permanen bata/batu yang tidak diplester',
                        'Ada, luas ventilasi < 10% dari luas lantai']
        buruk = ['Papan/anyaman bambu/plester retak berdebu', 'Ada tetapi tidak kedap air dan tidak tertutup']
        if val in sangat_buruk:
            return 2
        elif val in buruk:
            return 1
        else:
            return 0
    
    def nilai_sanitasi(val):
        if pd.isna(val):
            return 0
        sangat_buruk = ['Dibuang ke sungai/kebun/kolam/sembarangan', 'Tidak Ada',
                        'Tidak ada, sehingga tergenang dan tidak teratur di halaman/belakang rumah']
        buruk = ['Ada, tetapi tidak kedap air dan tidak tertutup', 'Ada, diresapkan tetapi mencemari sumber air (jarak <10m)']
        if any(sb in val for sb in sangat_buruk):
            return 2
        elif any(b in val for b in buruk):
            return 1
        else:
            return 0
    
    def nilai_perilaku(val):
        sangat_buruk = ['Tidak pernah', 'Ya', 'Tidak pernah dibuka', 'Tidak pernah CTPS']
        buruk = ['Kadang-kadang', 'Kadang-kadang dibuka', 'Kadang-kadang CTPS']
        if val in sangat_buruk:
            return 2
        elif val in buruk:
            return 1
        else:
            return 0
    
    rumah_kolom = ['langit_langit', 'lantai', 'dinding', 'ventilasi', 'lubang_asap_dapur', 'pencahayaan']
    sanitasi_kolom = ['sarana_pembuangan_air_limbah', 'sarana_pembuangan_sampah', 'membuang_tinja', 'membuang_sampah']
    perilaku_kolom = ['perilaku_merokok', 'anggota_keluarga_merokok', 'membersihkan_rumah', 'kebiasaan_ctps', 'memiliki_hewan_ternak']
    
    df_clean['skor_rumah'] = df_clean[rumah_kolom].apply(lambda col: col.map(nilai_rumah)).sum(axis=1)
    df_clean['skor_sanitasi'] = df_clean[sanitasi_kolom].apply(lambda col: col.map(nilai_sanitasi)).sum(axis=1)
    df_clean['skor_perilaku'] = df_clean[perilaku_kolom].apply(lambda col: col.map(nilai_perilaku)).sum(axis=1)
    
    df_clean['rumah_tidak_layak'] = df_clean['skor_rumah'] > 2
    df_clean['sanitasi_tidak_layak'] = df_clean['skor_sanitasi'] > 2
    df_clean['perilaku_tidak_baik'] = df_clean['skor_perilaku'] > 2
    
    st.markdown("### Hasil Pemberian Skor")
    st.write(df_clean[['skor_rumah', 'skor_sanitasi', 'skor_perilaku', 
                         'rumah_tidak_layak', 'sanitasi_tidak_layak', 'perilaku_tidak_baik']].head())
    
    # ----- 4. Visualisasi -----
    st.markdown("## Visualisasi Hasil Analisis")
    kategori_list = ["Rumah Tidak Layak", "Sanitasi Tidak Layak", "Perilaku Tidak Baik"]
    total_responden = len(df_clean)
    total_rumah_tidak_layak = df_clean['rumah_tidak_layak'].sum()
    total_sanitasi_tidak_layak = df_clean['sanitasi_tidak_layak'].sum()
    total_perilaku_tidak_baik = df_clean['perilaku_tidak_baik'].sum()
    persentase_list = [(total_rumah_tidak_layak / total_responden) * 100,
                        (total_sanitasi_tidak_layak / total_responden) * 100,
                        (total_perilaku_tidak_baik / total_responden) * 100]
    
    fig, ax = plt.subplots()
    ax.bar(kategori_list, persentase_list, color=['#E74C3C', '#FF7F0E', '#1F77B4'])
    ax.set_ylabel("Persentase (%)")
    ax.set_title("Persentase Kondisi Tidak Layak/Tidak Baik")
    for i, v in enumerate(persentase_list):
        ax.text(i, v + 2, f"{v:.2f}%", ha="center")
    st.pyplot(fig)
    
else:
    st.info("Silakan unggah file CSV atau Excel untuk memulai analisis.")
