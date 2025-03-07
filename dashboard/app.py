import streamlit as st
import pandas as pd

st.title("Analisis Kelayakan Rumah, Sanitasi, dan Perilaku Pasien TBC")

# Upload file CSV
df_file = st.file_uploader("Upload dataset CSV", type=["csv"])

if df_file is not None:
    try:
        # Mencoba membaca dengan delimiter otomatis
        df = pd.read_csv(df_file, encoding="utf-8", sep=None, engine="python")
        st.write("### Data Awal")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")


    # Identifikasi missing values
    missing_values = df.isnull().sum()
    missing_percentage = (missing_values / len(df)) * 100
    missing_data = pd.DataFrame({"Missing Values": missing_values, "Percentage": missing_percentage})
    missing_data = missing_data[missing_data["Missing Values"] > 0]
    st.write("### Missing Values")
    st.dataframe(missing_data.sort_values(by="Percentage", ascending=False))

    # Imputasi missing values
    kolom_numerik = df.select_dtypes(include=['number']).columns
    kolom_kategori = df.select_dtypes(include=['object']).columns
    
    # Mengisi missing values untuk kolom kategori dengan mode
    df[kolom_kategori] = df[kolom_kategori].apply(lambda x: x.fillna(x.mode()[0]))

    # Mengisi missing values untuk kolom numerik dengan mean (bisa diganti median jika diperlukan)
    df[kolom_numerik] = df[kolom_numerik].apply(lambda x: x.fillna(x.mean()))  # Bisa diganti x.median()

    st.write("### Data Setelah Imputasi")
    st.dataframe(df.head())

    # Definisi kategori
    kategori_rumah = ['status_rumah', 'langit_langit', 'lantai', 'dinding', 'jendela_kamar_tidur',
                       'jendela_ruang_keluarga', 'ventilasi', 'lubang_asap_dapur', 'pencahayaan']
    kategori_sanitasi = ['sarana_air_bersih', 'jamban', 'sarana_pembuangan_air_limbah',
                         'sarana_pembuangan_sampah', 'sampah']
    kategori_perilaku = ['perilaku_merokok', 'anggota_keluarga_merokok', 'membuka_jendela_kamar_tidur',
                         'membuka_jendela_ruang_keluarga', 'membersihkan_rumah', 'membuang_tinja',
                         'membuang_sampah', 'kebiasaan_ctps']
    
    df_rumah = df[kategori_rumah].dropna()
    df_sanitasi = df[kategori_sanitasi].dropna()
    df_perilaku = df[kategori_perilaku].dropna()

    # Fungsi hitung skor
    def hitung_skor(df, kategori, bobot):
        skor = []
        for index, row in df.iterrows():
            total_skor = sum(bobot.get(col, {}).get(row[col], 0) for col in kategori)
            max_skor = len(kategori) * 5
            skor.append((total_skor / max_skor) * 100 if max_skor > 0 else 0)
        df["Skor Kelayakan"] = skor
        return df

    # Bobot (contoh hanya untuk rumah)
    bobot_rumah = {
        "langit_langit": {"Ada": 5, "Tidak ada": 1},
        "lantai": {"Ubin/keramik/marmer": 5, "Tanah": 1},
        "dinding": {"Permanen (tembok pasangan batu bata yang diplester)": 5, "Bukan tembok": 1},
        "jendela_kamar_tidur": {"Ada": 5, "Tidak ada": 1},
        "jendela_ruang_keluarga": {"Ada": 5, "Tidak ada": 1},
        "ventilasi": {"Baik": 5, "Tidak Ada": 1},
        "lubang_asap_dapur": {"Ada": 5, "Tidak Ada": 1},
        "pencahayaan": {"Terang/Dapat digunakan membaca normal": 5, "Tidak Terang": 1}
    }
    
    df_rumah = hitung_skor(df_rumah, kategori_rumah, bobot_rumah)
    threshold = 70
    df_rumah["Label"] = df_rumah["Skor Kelayakan"].apply(lambda x: "Layak" if x >= threshold else "Tidak Layak")
    
    # Tampilkan hasil
    st.write("### Skor Kelayakan Rumah")
    st.dataframe(df_rumah.head())
    
    # Persentase Tidak Layak
    persentase_tidak_layak_rumah = (df_rumah[df_rumah["Label"] == "Tidak Layak"].shape[0] / df_rumah.shape[0]) * 100
    st.write(f"Persentase Rumah Tidak Layak: {persentase_tidak_layak_rumah:.2f}%")
