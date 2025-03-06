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
        # Baca file; jika CSV gunakan separator ";" sesuai file Anda
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
    df_clean = df_clean.dropna()  # Menghapus baris kosong
    df_clean.columns = df_clean.columns.str.strip()  # Membersihkan nama kolom
    st.write("Data setelah cleaning (5 baris pertama):", df_clean.head())
    
    # ----- 3. Fungsi Penilaian -----
    # Fungsi untuk penilaian Rumah
    def nilai_rumah(val):
        sangat_buruk = ['Tidak ada', 'Tanah', 'Kurang Baik', 'Bukan tembok', 'Tidak Ada',
                        'Kurang terang', 'Semi permanen bata/batu yang tidak diplester',
                        'Ada, luas ventilasi < 10% dari luas lantai']
        buruk = ['Papan/anyaman bambu/plester retak berdebu', 'Ada tetapi tidak kedap air dan tidak tertutup']
        if val in sangat_buruk:
            return 2  # Sangat Buruk
        elif val in buruk:
            return 1  # Buruk
        else:
            return 0  # Baik

    # Fungsi untuk penilaian Sanitasi
    def nilai_sanitasi(val):
        if pd.isna(val):  # Jika nilai NaN, anggap sebagai baik (0)
            return 0
        sangat_buruk = ['Dibuang ke sungai/kebun/kolam/sembarangan', 'Tidak Ada',
                        'Tidak ada, sehingga tergenang dan tidak teratur di halaman/belakang rumah']
        buruk = ['Ada, tetapi tidak kedap air dan tidak tertutup', 'Ada, diresapkan tetapi mencemari sumber air (jarak <10m)']
        if any(sb in val for sb in sangat_buruk):
            return 2  # Sangat Buruk
        elif any(b in val for b in buruk):
            return 1  # Buruk
        else:
            return 0  # Baik

    # Fungsi untuk penilaian Perilaku
    def nilai_perilaku(val):
        sangat_buruk = ['Tidak pernah', 'Ya', 'Tidak pernah dibuka', 'Tidak pernah CTPS']
        buruk = ['Kadang-kadang', 'Kadang-kadang dibuka', 'Kadang-kadang CTPS']
        if val in sangat_buruk:
            return 2  # Sangat Buruk
        elif val in buruk:
            return 1  # Buruk
        else:
            return 0  # Baik

    # ----- 4. Pemberian Skor -----
    # Pastikan kolom-kolom yang digunakan sesuai dengan file Anda
    rumah_kolom = ['langit_langit', 'lantai', 'dinding', 'ventilasi', 'lubang_asap_dapur', 'pencahayaan']
    sanitasi_kolom = ['sarana_pembuangan_air_limbah', 'sarana_pembuangan_sampah', 'membuang_tinja', 'membuang_sampah']
    perilaku_kolom = ['perilaku_merokok', 'anggota_keluarga_merokok', 'membersihkan_rumah', 'kebiasaan_ctps', 'memiliki_hewan_ternak']
    
    # Hitung skor untuk setiap kategori
    df_clean['skor_rumah'] = df_clean[rumah_kolom].apply(lambda col: col.map(nilai_rumah)).sum(axis=1)
    df_clean['skor_sanitasi'] = df_clean[sanitasi_kolom].apply(lambda col: col.map(nilai_sanitasi)).sum(axis=1)
    df_clean['skor_perilaku'] = df_clean[perilaku_kolom].apply(lambda col: col.map(nilai_perilaku)).sum(axis=1)
    
    # Tentukan apakah responden tergolong tidak layak/tidak baik (threshold > 2)
    df_clean['rumah_tidak_layak'] = df_clean['skor_rumah'] > 2
    df_clean['sanitasi_tidak_layak'] = df_clean['skor_sanitasi'] > 2
    df_clean['perilaku_tidak_baik'] = df_clean['skor_perilaku'] > 2
    
    st.markdown("### Hasil Pemberian Skor")
    st.write(df_clean[['skor_rumah', 'skor_sanitasi', 'skor_perilaku', 
                         'rumah_tidak_layak', 'sanitasi_tidak_layak', 'perilaku_tidak_baik']].head())
    
    # Hitung total dan persentase untuk masing-masing kategori
    total_responden = len(df_clean)
    total_rumah_tidak_layak = df_clean['rumah_tidak_layak'].sum()
    total_sanitasi_tidak_layak = df_clean['sanitasi_tidak_layak'].sum()
    total_perilaku_tidak_baik = df_clean['perilaku_tidak_baik'].sum()
    
    persentase_tidak_layak_rumah = (total_rumah_tidak_layak / total_responden) * 100
    persentase_tidak_layak_sanitasi = (total_sanitasi_tidak_layak / total_responden) * 100
    persentase_tidak_baik_perilaku = (total_perilaku_tidak_baik / total_responden) * 100

    st.markdown("### Statistik Kondisi")
    st.write(f"Persentase Rumah Tidak Layak: {persentase_tidak_layak_rumah:.2f}%")
    st.write(f"Persentase Sanitasi Tidak Layak: {persentase_tidak_layak_sanitasi:.2f}%")
    st.write(f"Persentase Perilaku Tidak Baik: {persentase_tidak_baik_perilaku:.2f}%")
    
    # ----- 5. Visualisasi -----
    st.markdown("## Visualisasi Hasil Analisis")
    
    # A. Bar Chart untuk ketiga kategori
    kategori_list = ["Rumah Tidak Layak", "Sanitasi Tidak Layak", "Perilaku Tidak Baik"]
    persentase_list = [persentase_tidak_layak_rumah, persentase_tidak_layak_sanitasi, persentase_tidak_baik_perilaku]
    
    # Urutkan kategori dari yang tertinggi ke terendah
    sorted_indices = sorted(range(len(persentase_list)), key=lambda i: persentase_list[i], reverse=True)
    kategori_sorted = [kategori_list[i] for i in sorted_indices]
    persentase_sorted = [persentase_list[i] for i in sorted_indices]
    
    fig1, ax1 = plt.subplots(figsize=(8,5))
    bars = ax1.bar(kategori_sorted, persentase_sorted, color=['#E74C3C', '#FF7F0E', '#1F77B4'])
    ax1.set_xlabel("Kategori")
    ax1.set_ylabel("Persentase (%)")
    ax1.set_title("Persentase Kondisi Tidak Layak/Tidak Baik")
    ax1.set_ylim(0, 100)
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    for i, v in enumerate(persentase_sorted):
        ax1.text(i, v + 2, f"{v:.2f}%", ha="center", fontsize=10)
    st.pyplot(fig1)
    
    # B. Visualisasi khusus untuk Sanitasi Tidak Layak
    st.markdown("### Visualisasi Faktor Sanitasi Tidak Layak")
    df_sanitasi = df_clean[df_clean['sanitasi_tidak_layak']]
    if not df_sanitasi.empty:
        # Hitung distribusi nilai untuk masing-masing kolom sanitasi
        sanitasi_counts = df_sanitasi[sanitasi_kolom].apply(lambda col: col.map(nilai_sanitasi)).sum()
        # Hitung persentase tiap faktor dari total kasus sanitasi tidak layak
        sanitasi_persen = (sanitasi_counts / sanitasi_counts.sum()) * 100
        sanitasi_persen = sanitasi_persen.sort_values(ascending=False)
        
        fig2, ax2 = plt.subplots(figsize=(10,6))
        bars2 = ax2.barh(sanitasi_persen.index, sanitasi_persen.values, color='#3498DB', alpha=0.7)
        ax2.set_xlabel("Persentase (%)")
        ax2.set_ylabel("Faktor Sanitasi Tidak Baik")
        ax2.set_title(f"{persentase_tidak_layak_sanitasi:.0f}% Sanitasi Tidak Layak")
        ax2.invert_yaxis()  # Faktor terbesar di atas
        ax2.grid(axis="x", linestyle="--", alpha=0.7)
        for bar in bars2:
            ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                     f"{bar.get_width():.2f}%", va='center', fontsize=10, fontweight="bold")
        st.pyplot(fig2)
    else:
        st.info("Tidak ada data untuk sanitasi tidak layak guna visualisasi faktor sanitasi.")

else:
    st.info("Silakan unggah file CSV atau Excel untuk memulai analisis.")

