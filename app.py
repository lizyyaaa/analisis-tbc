import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Fungsi untuk memberi skor
def nilai_rumah(val):
    if val in ['Baik', 'Layak']: return 0
    elif val in ['Kurang Baik', 'Tidak Layak']: return 1
    return None  # Jika nilai tidak dikenali

def nilai_sanitasi(val):
    if val in ['Baik']: return 0
    elif val in ['Kurang', 'Tidak Layak']: return 1
    return None

def nilai_perilaku(val):
    if val in ['Baik']: return 0
    elif val in ['Kurang', 'Buruk']: return 1
    return None

# Streamlit UI
st.title("Analisis Data Pasien TBC")

uploaded_file = st.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Baca file CSV atau Excel
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine="python")
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File berhasil diunggah!")
        st.write("Jumlah Baris & Kolom:", df.shape)
        st.write("Kolom yang tersedia:", df.columns.tolist())
        st.write("Data asli (5 baris pertama):", df.head())

        # Tentukan kolom untuk setiap kategori
        rumah_kolom = ['Kondisi Rumah']  # Ganti dengan nama kolom asli
        sanitasi_kolom = ['Sanitasi']  # Ganti dengan nama kolom asli
        perilaku_kolom = ['Perilaku']  # Ganti dengan nama kolom asli

        # Cek apakah kolom yang dibutuhkan ada
        missing_columns = [col for col in rumah_kolom + sanitasi_kolom + perilaku_kolom if col not in df.columns]
        if missing_columns:
            st.error(f"Kolom berikut tidak ditemukan dalam data: {missing_columns}")
            st.stop()

        # Cleaning data (hapus NaN yang tidak diperlukan)
        df_clean = df.dropna(how='all')

        # Beri skor untuk setiap kategori
        df_clean['skor_rumah'] = df_clean[rumah_kolom[0]].map(nilai_rumah)
        df_clean['skor_sanitasi'] = df_clean[sanitasi_kolom[0]].map(nilai_sanitasi)
        df_clean['skor_perilaku'] = df_clean[perilaku_kolom[0]].map(nilai_perilaku)

        # Cek apakah ada NaN setelah pemetaan
        st.write("Jumlah NaN dalam Skor Rumah:", df_clean['skor_rumah'].isna().sum())
        st.write("Jumlah NaN dalam Skor Sanitasi:", df_clean['skor_sanitasi'].isna().sum())
        st.write("Jumlah NaN dalam Skor Perilaku:", df_clean['skor_perilaku'].isna().sum())

        # Pastikan tidak ada NaN
        df_clean = df_clean.dropna(subset=['skor_rumah', 'skor_sanitasi', 'skor_perilaku'])

        st.write("Data setelah cleaning (5 baris pertama):", df_clean.head())

        # Hitung persentase kondisi tidak layak
        total_data = len(df_clean)
        if total_data == 0:
            st.error("Data kosong setelah cleaning. Pastikan file yang diunggah benar.")
            st.stop()

        persen_rumah = (df_clean['skor_rumah'].sum() / total_data) * 100
        persen_sanitasi = (df_clean['skor_sanitasi'].sum() / total_data) * 100
        persen_perilaku = (df_clean['skor_perilaku'].sum() / total_data) * 100

        # Tampilkan hasil analisis
        st.subheader("Hasil Pemberian Skor")
        st.write("Statistik Kondisi")
        st.write(f"Persentase Rumah Tidak Layak: {persen_rumah:.2f}%")
        st.write(f"Persentase Sanitasi Tidak Layak: {persen_sanitasi:.2f}%")
        st.write(f"Persentase Perilaku Tidak Baik: {persen_perilaku:.2f}%")

        # Visualisasi Hasil Analisis
        st.subheader("Visualisasi Hasil Analisis")
        
        kategori = ["Rumah Tidak Layak", "Sanitasi Tidak Layak", "Perilaku Tidak Baik"]
        persentase = [persen_rumah, persen_sanitasi, persen_perilaku]

        if any(pd.isna(persentase)):  # Cek apakah ada NaN
            st.error("Data tidak valid untuk visualisasi. Pastikan semua skor telah dihitung.")
        else:
            fig1, ax1 = plt.subplots(figsize=(8,5))
            ax1.bar(kategori, persentase, color=['#E74C3C', '#FF7F0E', '#1F77B4'])
            ax1.set_xlabel("Kategori")
            ax1.set_ylabel("Persentase (%)")
            ax1.set_title("Persentase Kondisi Tidak Layak/Tidak Baik")
            ax1.set_ylim(0, 100)
            ax1.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(fig1)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
